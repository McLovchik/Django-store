from django import forms
from .models import Order


class OrderingStepOneForm(forms.ModelForm):
    """
    Order progress first step form. Adding fullname, phone and email
    to order information.
    """
    fullname = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input'
    }))
    phone = forms.CharField(widget=forms.NumberInput(attrs={
        'class': 'form-input'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-input'
    }))

    class Meta:
        model = Order
        fields = ['fullname', 'phone', 'email']


class OrderingStepTwoForm(forms.ModelForm):
    """
    Order progress second step form. Adding delivery type, city and address
    to order information.
    """
    class Meta:
        model = Order
        widgets = {
            'delivery': forms.RadioSelect(
                attrs={
                    'class': 'toggle-box'
                }
            ),
            'city': forms.TextInput(
                attrs={
                    'class': 'form-input'
                }
            ),
            'address': forms.Textarea(
                attrs={
                    'class': 'form-textarea'
                }
            )
        }
        fields = ['delivery', 'city', 'address']


class OrderingStepThreeForm(forms.ModelForm):
    """
    Order progress third step form. Adding payment method
    to order information.
    """

    class Meta:
        model = Order
        widgets = {
            'payment_method': forms.RadioSelect(
                attrs={
                    'class': 'toggle-box'
                }
            ),
        }
        fields = ['payment_method']
