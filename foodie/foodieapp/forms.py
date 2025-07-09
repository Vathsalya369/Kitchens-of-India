# forms.py
from django import forms
from django.contrib.auth.forms import User, PasswordResetForm, SetPasswordForm
from django.core.exceptions import ValidationError
from .models import Restaurant, MenuItem, Category

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Password', 'id': 'id_password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm Password'
    }))
    
    class Meta:
        model = User
        fields = ['first_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email is already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")
    

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Email', 'class': 'form-control'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Password', 'class': 'form-control', 'id':'password'
    }))

class RestaurantForm(forms.ModelForm):
    class Meta:
        model=Restaurant
        fields=['name', 'city', 'image', 'address', 'phone', 'rating', 'is_active', 'delivery_time']
    
class MenuItemForm(forms.ModelForm):
    class Meta:
        model=MenuItem 
        fields=['restaurant', 'category', 'name', 'price', 'image', 'description', 'is_vegetarian', 'is_available', 'is_popular']

class CategoryItem(forms.ModelForm):
    class Meta:
        model=Category
        fields=['name', 'icon', 'is_active']

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Enter your registered email',
        'class': 'form-control'
    }))

class SetNewPasswordForm(forms.Form):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'New password','class':'form-control'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password','class':'form-control'})
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_new_password2(self):
        p1 = self.cleaned_data.get('new_password1')
        p2 = self.cleaned_data.get('new_password2')
        if p1 != p2:
            raise ValidationError("Passwords don’t match.")
        if self.user.check_password(p1):
            raise ValidationError("New password must differ from the old one.")
        return p2