from django.urls import path
from . import views

app_name = 'shop'  # enables namespaced URLs, e.g. {% url 'shop:menu' %}

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('menu/', views.menu, name='menu'),

    # Cart
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:item_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:item_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),

    # Checkout & confirmation
    path('checkout/', views.checkout, name='checkout'),
    path('order/<int:order_id>/success/', views.order_success, name='order_success'),

    # Owner dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/order/<int:order_id>/status/', views.dashboard_update_status, name='dashboard_update_status'),
    path('dashboard/order/<int:order_id>/delete/', views.dashboard_delete_order, name='dashboard_delete_order'),
]
