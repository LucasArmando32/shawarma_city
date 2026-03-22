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
                'placeholder': 'Dein Name',
                'class': 'form-control',
            }),
            'customer_phone': forms.TextInput(attrs={
                'placeholder': 'Telefonnummer',
                'class': 'form-control',
            }),
            'order_type': forms.RadioSelect(attrs={
                'class': 'order-type-radio',
            }),
            'customer_address': forms.Textarea(attrs={
                'placeholder': 'Lieferadresse (nur bei Lieferung nötig)',
                'rows': 3,
                'class': 'form-control',
            }),
            'notes': forms.Textarea(attrs={
                'placeholder': 'Besondere Wünsche? z.B. ohne Zwiebeln, extra Sauce...',
                'rows': 3,
                'class': 'form-control',
            }),
        }
        labels = {
            'customer_name': 'Dein Name',
            'customer_phone': 'Telefonnummer',
            'order_type': 'Wie möchtest du deine Bestellung erhalten?',
            'customer_address': 'Lieferadresse',
            'notes': 'Anmerkungen für die Küche',
        }

    def clean(self):
        cleaned_data = super().clean()
        order_type = cleaned_data.get('order_type')
        address = cleaned_data.get('customer_address')

        # Address is required only when the customer chooses delivery
        if order_type == Order.OrderType.DELIVERY and not address:
            self.add_error('customer_address', 'Bitte gib eine Lieferadresse an.')

        return cleaned_data
