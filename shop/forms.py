from django import forms
from .models import Order


class CheckoutForm(forms.ModelForm):
    """
    The form the customer fills in to place their order.
    The cart contents (items + quantities) come from the session,
    not from this form — this form is only for customer info.
    """

    class Meta:
        model = Order
        fields = [
            'customer_name',
            'customer_phone',
            'order_type',
            'customer_address',
            'notes',
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'placeholder': 'Your name',
                'class': 'form-control',
            }),
            'customer_phone': forms.TextInput(attrs={
                'placeholder': 'Phone number',
                'class': 'form-control',
            }),
            'order_type': forms.RadioSelect(attrs={
                'class': 'order-type-radio',
            }),
            'customer_address': forms.Textarea(attrs={
                'placeholder': 'Delivery address (only needed for delivery)',
                'rows': 3,
                'class': 'form-control',
            }),
            'notes': forms.Textarea(attrs={
                'placeholder': 'Any special requests? e.g. no onions, extra sauce...',
                'rows': 3,
                'class': 'form-control',
            }),
        }
        labels = {
            'customer_name': 'Your Name',
            'customer_phone': 'Phone Number',
            'order_type': 'How would you like to receive your order?',
            'customer_address': 'Delivery Address',
            'notes': 'Notes for the kitchen',
        }

    def clean(self):
        cleaned_data = super().clean()
        order_type = cleaned_data.get('order_type')
        address = cleaned_data.get('customer_address')

        # Address is required only when the customer chooses delivery
        if order_type == Order.OrderType.DELIVERY and not address:
            self.add_error('customer_address', 'Please provide a delivery address.')

        return cleaned_data
