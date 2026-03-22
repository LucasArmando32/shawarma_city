from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import Category, MenuItem, Order, OrderItem
from .forms import CheckoutForm


# ---------------------------------------------------------------------------
# Cart helpers
# The cart lives in the Django session as a plain dictionary:
#   session['cart'] = { "<menu_item_id>": <quantity>, ... }
# No database writes happen until the customer actually places the order.
# ---------------------------------------------------------------------------

def _get_cart(request):
    """Returns the cart dict from the session, creating it if it doesn't exist."""
    return request.session.setdefault('cart', {})


def _cart_item_count(request):
    """Returns the total number of items (sum of quantities) in the cart."""
    return sum(_get_cart(request).values())


def _cart_details(request):
    """
    Returns a list of dicts with full item info for rendering the cart,
    plus the overall total price.
    """
    cart = _get_cart(request)
    if not cart:
        return [], 0

    item_ids = [int(k) for k in cart.keys()]
    menu_items = MenuItem.objects.filter(pk__in=item_ids).select_related('category')
    menu_items_map = {item.pk: item for item in menu_items}

    lines = []
    total = 0
    for item_id_str, quantity in cart.items():
        item_id = int(item_id_str)
        menu_item = menu_items_map.get(item_id)
        if menu_item:
            subtotal = menu_item.price * quantity
            total += subtotal
            lines.append({
                'menu_item': menu_item,
                'quantity': quantity,
                'subtotal': subtotal,
            })

    return lines, total


# ---------------------------------------------------------------------------
# Public views
# ---------------------------------------------------------------------------

def home(request):
    """
    Landing page. Shows a brief intro and a few featured items from each category.
    """
    categories = Category.objects.prefetch_related('items').all()

    # Show up to 4 available items per category as a preview
    featured = []
    for category in categories:
        items = list(category.items.filter(available=True)[:4])
        if items:
            featured.append({'category': category, 'items': items})

    context = {
        'featured': featured,
        'cart_count': _cart_item_count(request),
    }
    return render(request, 'shop/home.html', context)


def menu(request):
    """
    Full menu page, grouped by category.
    The template renders Food and Drinks as separate tabs/sections.
    """
    categories = Category.objects.prefetch_related(
        'items'
    ).all()

    # Only show categories that have at least one available item
    menu_data = []
    for category in categories:
        items = list(category.items.filter(available=True))
        if items:
            menu_data.append({'category': category, 'items': items})

    context = {
        'menu_data': menu_data,
        'cart_count': _cart_item_count(request),
    }
    return render(request, 'shop/menu.html', context)


def cart(request):
    """
    Cart page. Shows everything the customer has added so far
    and lets them adjust quantities or remove items.
    """
    lines, total = _cart_details(request)
    context = {
        'lines': lines,
        'total': total,
        'cart_count': _cart_item_count(request),
    }
    return render(request, 'shop/cart.html', context)


@require_POST
def cart_add(request, item_id):
    """
    Adds one unit of a menu item to the cart (or increments quantity).
    Called via a POST from the menu page or the cart page.
    """
    menu_item = get_object_or_404(MenuItem, pk=item_id, available=True)
    cart = _get_cart(request)
    key = str(menu_item.pk)
    cart[key] = cart.get(key, 0) + 1
    request.session.modified = True
    messages.success(request, f'"{menu_item.name}" wurde zum Warenkorb hinzugefügt.')
    return redirect(request.META.get('HTTP_REFERER', 'shop:menu'))


@require_POST
def cart_update(request, item_id):
    """
    Updates the quantity of an item in the cart.
    Quantity 0 removes the item entirely.
    """
    cart = _get_cart(request)
    key = str(item_id)
    quantity = int(request.POST.get('quantity', 0))

    if quantity <= 0:
        cart.pop(key, None)
    else:
        cart[key] = quantity

    request.session.modified = True
    return redirect('shop:cart')


@require_POST
def cart_remove(request, item_id):
    """Removes an item from the cart entirely."""
    cart = _get_cart(request)
    cart.pop(str(item_id), None)
    request.session.modified = True
    return redirect('shop:cart')


def checkout(request):
    """
    Checkout page. Shows the cart summary and the customer info form.
    On POST: validates the form, creates the Order and OrderItems in the DB,
    clears the cart, and redirects to the success page.
    """
    lines, total = _cart_details(request)

    if not lines:
        messages.warning(request, 'Dein Warenkorb ist leer.')
        return redirect('shop:menu')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.total_price = total
            order.save()

            # Create an OrderItem for each line in the cart
            for line in lines:
                OrderItem.objects.create(
                    order=order,
                    menu_item=line['menu_item'],
                    quantity=line['quantity'],
                    unit_price=line['menu_item'].price,
                )

            # Clear the cart from the session
            request.session['cart'] = {}
            request.session.modified = True

            return redirect('shop:order_success', order_id=order.pk)
    else:
        form = CheckoutForm()

    context = {
        'form': form,
        'lines': lines,
        'total': total,
        'cart_count': _cart_item_count(request),
    }
    return render(request, 'shop/checkout.html', context)


def order_success(request, order_id):
    """
    Confirmation page shown after a successful order.
    Displays the order number and a summary.
    """
    order = get_object_or_404(Order, pk=order_id)
    context = {
        'order': order,
        'cart_count': 0,
    }
    return render(request, 'shop/order_success.html', context)


# ---------------------------------------------------------------------------
# Owner Dashboard — only accessible to staff/admin users
# ---------------------------------------------------------------------------

@staff_member_required(login_url='/admin/login/')
def dashboard(request):
    """
    Einfaches Besitzer-Dashboard.
    Zeigt alle Bestellungen von heute und offene Bestellungen.
    """
    today = timezone.localdate()

    orders_today   = Order.objects.filter(created_at__date=today).order_by('-created_at')
    orders_open    = Order.objects.filter(
        status__in=[Order.Status.PENDING, Order.Status.CONFIRMED]
    ).order_by('-created_at')
    orders_ready   = Order.objects.filter(status=Order.Status.READY).order_by('-created_at')

    # Stats
    total_today    = sum(o.total_price for o in orders_today)
    count_pending  = orders_open.filter(status=Order.Status.PENDING).count()
    count_today    = orders_today.count()

    context = {
        'orders_open':   orders_open,
        'orders_ready':  orders_ready,
        'orders_today':  orders_today,
        'total_today':   total_today,
        'count_pending': count_pending,
        'count_today':   count_today,
        'cart_count':    0,
        'Status':        Order.Status,
    }
    return render(request, 'shop/dashboard.html', context)


@staff_member_required(login_url='/admin/login/')
@require_POST
def dashboard_delete_order(request, order_id):
    """Löscht eine Bestellung direkt vom Dashboard aus."""
    order = get_object_or_404(Order, pk=order_id)
    order.delete()
    messages.success(request, f'Bestellung #{order_id} wurde gelöscht.')
    return redirect('shop:dashboard')


@staff_member_required(login_url='/admin/login/')
@require_POST
def dashboard_update_status(request, order_id):
    """Ändert den Status einer Bestellung direkt vom Dashboard aus."""
    order     = get_object_or_404(Order, pk=order_id)
    new_status = request.POST.get('status')
    if new_status in Order.Status.values:
        order.status = new_status
        order.save(update_fields=['status'])
        messages.success(request, f'Bestellung #{order.pk} → {order.get_status_display()}')
    return redirect('shop:dashboard')
