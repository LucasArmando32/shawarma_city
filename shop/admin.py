from django.contrib import admin
from .models import Category, MenuItem, Order, OrderItem

# Custom admin site titles (German)
admin.site.site_header  = '🔥 Shawarma Falafel City — Verwaltung'
admin.site.site_title   = 'Shawarma Falafel City'
admin.site.index_title  = 'Willkommen im Verwaltungsbereich'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}  # auto-fills slug from name
    ordering = ('order', 'name')


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'available', 'order')
    list_filter = ('category', 'available')
    list_editable = ('price', 'available', 'order')  # edit directly in the list
    search_fields = ('name', 'description')
    ordering = ('category', 'order', 'name')


class OrderItemInline(admin.TabularInline):
    """Shows order items directly inside the order detail page."""
    model = OrderItem
    extra = 0
    readonly_fields = ('menu_item', 'quantity', 'unit_price', 'subtotal')

    def subtotal(self, obj):
        return obj.subtotal
    subtotal.short_description = 'Subtotal'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'customer_name', 'customer_phone',
        'order_type', 'status', 'total_price', 'created_at'
    )
    list_filter = ('status', 'order_type')
    list_editable = ('status',)  # shop owner can update status directly in the list
    search_fields = ('customer_name', 'customer_phone')
    readonly_fields = ('created_at', 'updated_at', 'total_price')
    ordering = ('-created_at',)
    inlines = [OrderItemInline]
