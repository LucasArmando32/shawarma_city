from django.db import models


class Category(models.Model):
    """
    Represents a menu category, e.g. 'Food' or 'Drinks'.
    Using a model (instead of hardcoding) means you can add
    'Sides', 'Desserts', etc. later without changing any code.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)  # used in URLs, e.g. 'food', 'drinks'
    order = models.PositiveIntegerField(default=0)  # controls display order

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Kategorie'
        verbose_name_plural = 'Kategorien'

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    """
    A single item on the menu (e.g. Chicken Kebab, Ayran).
    """
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='items'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='menu/', blank=True, null=True)
    available = models.BooleanField(default=True)  # toggle to hide sold-out items
    order = models.PositiveIntegerField(default=0)  # controls display order within category

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Menü-Artikel'
        verbose_name_plural = 'Menü-Artikel'

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class Order(models.Model):
    """
    A customer order. No user account required — just a name and phone number.
    The shop owner can update the status from the admin panel.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'Ausstehend'
        CONFIRMED = 'confirmed', 'Bestätigt'
        READY = 'ready', 'Bereit zur Abholung'
        DELIVERED = 'delivered', 'Geliefert'
        CANCELLED = 'cancelled', 'Storniert'

    class OrderType(models.TextChoices):
        PICKUP = 'pickup', 'Abholung'
        DELIVERY = 'delivery', 'Lieferung'

    # Customer info
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=20)
    customer_address = models.TextField(blank=True)  # only needed for delivery

    # Order details
    order_type = models.CharField(
        max_length=10,
        choices=OrderType.choices,
        default=OrderType.PICKUP
    )
    notes = models.TextField(blank=True)  # e.g. "no onions please"
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDING
    )
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Bestellung'
        verbose_name_plural = 'Bestellungen'

    def __str__(self):
        return f"Bestellung #{self.pk} — {self.customer_name} ({self.status})"

    def calculate_total(self):
        """Recalculates and saves the total from all order items."""
        total = sum(item.subtotal for item in self.items.all())
        self.total_price = total
        self.save(update_fields=['total_price'])
        return total


class OrderItem(models.Model):
    """
    A single line in an order: which menu item, how many, and at what price.
    We store the price at time of order so that later price changes don't
    affect historical orders.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.PROTECT,  # PROTECT: don't delete menu items that appear in orders
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)  # price at time of order

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity
