from django import forms
from .models import ProductImage, ProductComment
from django.forms import ClearableFileInput, TextInput, Textarea


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']
        widgets = {
            'image': ClearableFileInput(attrs={'multiple': True}),
        }


class ReviewForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        self.fields['product'].widget = forms.HiddenInput()
        self.fields['content'].label = False
        self.fields['author_name'].label = False

    class Meta:
        model = ProductComment
        fields = ['product', 'user', 'author_name', 'content']
        exclude = ['added', ]
        widgets = {
            'content': Textarea(attrs={
                'placeholder': 'Review',
                'class': 'form-textarea'
            }),
            'author_name': TextInput(attrs={
                'placeholder': 'Name',
                'class': 'form-input custom-form-input-for-detail-product-page'
            })
        }
