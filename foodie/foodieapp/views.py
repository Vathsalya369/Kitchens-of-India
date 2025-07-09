from django.conf import settings
from django import forms

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db.models import Q 
from django.contrib import messages
# from .forms import InputForm
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .forms import SignupForm, LoginForm, RestaurantForm, MenuItemForm, CategoryItem, ForgotPasswordForm, SetNewPasswordForm
from django.contrib.auth import authenticate, login
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from .models import City, Restaurant, MenuItem, Partner

from collections import defaultdict

import json
import random
import os

# Create your views here.

def staticWebsite(request):
    search_query = request.GET.get('search', '').strip()
    show_alert = False

    if search_query:
        cities = City.objects.filter(
            name__icontains=search_query,
            restaurant__is_active=True
        ).distinct().order_by('name')

        if not cities.exists():
            show_alert = True
    else:
        cities = City.objects.filter(
            restaurant__is_active=True
        ).distinct().order_by('name')

    return render(request, 'staticWebsiteChild.html', {
        'cities': cities,
        'show_alert': show_alert,
        'search_query': search_query,
    })


def restaurant_list(request, city_name):
    # city=City.objects.get(name=city_name)
    city = get_object_or_404(City, name=city_name)

    restaurants=Restaurant.objects.filter(city=city)
    query=request.GET.get('search')
    if query:
        restaurants=restaurants.filter(name__icontains=query)
        if not restaurants.exists():
            messages.warning(request, f"No restaurant found matching '{query}' in {city.name}. ")
    return render(request, 'restaurant_list.html', {'city':city, 'restaurants':restaurants})

def menu_view(request, restaurant_id):
    print("Current session cart:", request.session.get('cart', {}))
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    menu_items = MenuItem.objects.filter(restaurant=restaurant)

    grouped_menu = defaultdict(list)
    for item in menu_items:
        grouped_menu[item.category.name if item.category else "Uncategorized"].append(item)

    request.session['last_restaurant_id'] = restaurant_id

    # ✅ Get cart from session
    cart = request.session.get('cart', {})

    # ✅ If cart is empty, clean it fully from session
    if not cart:
        request.session['cart'] = {}

    return render(request, 'menu_list.html', {
        'restaurant': restaurant,
        'grouped_menu': dict(grouped_menu),
        'is_partner': False,
        'cart': request.session.get('cart', {}),
    })



# def signup(request):
#     return render(request, "signup.html")

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']  # optional
            user.password = make_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')  # adjust this name
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})  # <--- important

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            users = User.objects.filter(email=email)
            if not users.exists():
                form.add_error('email', 'Email is not registered')
            elif users.count() > 1:
                form.add_error('email', 'Multiple accounts found with this email. Please contact support.')
            else:
                user = users.first()
                if user.check_password(password):
                    login(request, user)
                    return redirect('staticWebsite')
                else:
                    form.add_error('password', 'Incorrect password')
    else:
        form = LoginForm()
        
    return render(request, 'login.html', {'form': form})

def clean_email(self):
    email = self.cleaned_data['email']
    if User.objects.filter(email=email).exists():
        raise forms.ValidationError("Email is already registered.")
    return email


def partner_login(request):
    if request.method == 'POST':
        contact = request.POST.get('contact')
        otp = str(random.randint(100000, 999999))
        request.session['contact'] = contact
        request.session['otp'] = otp
        print("OTP:", otp)
        return redirect('verify_otp')

    return render(request, 'partner.html')


def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')
        contact = request.session.get('contact')

        if entered_otp == session_otp:
            return HttpResponse(f"✅ OTP verified! Logged in as {contact}")
        else:
            return HttpResponse("❌ Incorrect OTP. Please try again.")

    return render(request, 'verify_otp.html')

def city_not_found(request):
    return render(request, 'city_not_found.html')

from decouple import config
import os

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = config("TWILIO_AUTH_TOKEN")
VERIFY_SERVICE_SID = config("VERIFY_SERVICE_SID")


client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

# View to display form and send OTP
from twilio.base.exceptions import TwilioRestException

import re
from twilio.base.exceptions import TwilioRestException

def normalize_phone_number(phone):
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)

    # Add +91 if not present
    if digits.startswith('91') and len(digits) == 12:
        return '+' + digits
    elif len(digits) == 10:
        return '+91' + digits
    elif digits.startswith('+91') and len(digits) == 13:
        return digits
    else:
        # fallback to +91 and last 10 digits (for malformed)
        return '+91' + digits[-10:]

def partner_send_otp(request):
    if request.method == 'POST':
        raw_phone = request.POST.get('phone')
        phone = normalize_phone_number(raw_phone)
        request.session['phone'] = phone

        try:
            client.verify.v2.services(VERIFY_SERVICE_SID).verifications.create(
                to=phone,
                channel='sms'
            )
            return redirect('partner_verify_otp')
        except TwilioRestException as e:
            return HttpResponse(f"❌ Cannot send OTP: {e.msg} (trial accounts can only send to verified numbers)")

    return render(request, 'partner_send_otp.html')


# View to verify entered OTP
from django.shortcuts import redirect
from .models import Partner

def partner_verify_otp(request):
    if request.method == 'POST':
        phone = request.session.get('phone')
        otp = request.POST.get('otp')

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)   #-------------------------------------------------------

        try:
            verification_check = client.verify.v2.services(settings.VERIFY_SERVICE_SID).verification_checks.create(
                to=phone,
                code=otp
            )
        except TwilioRestException as e:
            return HttpResponse(f"Verification failed: {e.msg}")

        if verification_check.status == "approved":
            request.session['partner_logged_in'] = True
            request.session['partner_phone'] = phone
            Partner.objects.get_or_create(phone=phone)

            return redirect('enter_city')

        else:
            return HttpResponse("❌ Invalid OTP. Try again.")

    return render(request, 'partner_verify_otp.html')

def add_restaurant(request):
    if not request.session.get('partner_logged_in'):
        return redirect('partner_login')

    partner_phone = request.session.get('partner_phone')
    restaurants = Restaurant.objects.filter(phone=partner_phone)  # ✅ Now always defined

    if request.method == 'POST':
        form = RestaurantForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name'].strip()
            city_id = request.session.get('partner_city_id')
            city = City.objects.get(id=city_id)

            if Restaurant.objects.filter(name__iexact=name, phone=partner_phone, city=city).exists():
                messages.warning(request, "⚠️ Restaurant with this name already exists in your city.")
            else:
                restaurant = form.save(commit=False)
                restaurant.phone = partner_phone
                restaurant.city = city
                restaurant.save()
                messages.success(request, "✅ Restaurant added successfully!")
                return redirect('add_menu', restaurant_id=restaurant.id)
    else:
        form = RestaurantForm()

    return render(request, 'add_restaurant.html', {'form': form, 'restaurants': restaurants})

def enter_city(request):
    if request.method == 'POST':
        city_name = request.POST.get('city').strip()
        if city_name:
            city, created = City.objects.get_or_create(name=city_name.title())
            request.session['partner_city_id'] = city.id  # Save city in session
            return redirect('add_restaurant') # or wherever you want next
    return render(request, 'enter_city.html')

# @require_POST
def delete_restaurant(request, restaurant_id):
    try:
        restaurant = Restaurant.objects.get(id=restaurant_id)
    except Restaurant.DoesNotExist:
        messages.error(request, "❌ Restaurant not found.")
        return redirect('staticWebsite')

    if request.session.get('partner_logged_in') and restaurant.phone == request.session.get('partner_phone'):
        restaurant.delete()
        messages.success(request, "✅ Restaurant deleted successfully.")
    else:
        messages.error(request, "❌ You don't have permission to delete this restaurant.")

    city_id = request.session.get('selected_city_id') or request.session.get('partner_city_id')
    if city_id:
        city = City.objects.get(id=city_id)
        return redirect('restaurant_list', city_name=city.name)

    return redirect('staticWebsite')

# def add_menu_item(request, restaurant_id):
#     if not request.session.get('partner_logged_in'):
#         return redirect('partner_login')

#     restaurant = get_object_or_404(Restaurant, id=restaurant_id)

#     # Check ownership
#     if restaurant.phone != request.session.get('partner_phone'):
#         messages.warning(request, "You are not authorized to add items to this restaurant.")
#         return redirect('restaurant_list')

#     if request.method == 'POST':
#         form = MenuItemForm(request.POST, request.FILES)
#         if form.is_valid():
#             menu_item = form.save(commit=False)
#             menu_item.restaurant = restaurant
#             menu_item.save()
#             messages.success(request, "✅ Menu item added successfully!")
#             return redirect('menu', restaurant_id=restaurant.id)
#     else:
#         form = MenuItemForm()

#     return render(request, 'add_menu_item.html', {'form': form, 'restaurant': restaurant})

# from django.shortcuts import render, redirect, get_object_or_404
# from .models import Restaurant, MenuItem
# from .forms import MenuItemForm
# from django.contrib import messages

def add_menu(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    if not request.session.get('partner_logged_in') or restaurant.phone != request.session.get('partner_phone'):
        return redirect('partner_login')

    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            menu_item = form.save(commit=False)
            menu_item.restaurant = restaurant
            menu_item.save()
            messages.success(request, "✅ Menu item added successfully!")
            return redirect('add_menu', restaurant_id=restaurant.id)
    else:
        form = MenuItemForm()

    menu_items = MenuItem.objects.filter(restaurant=restaurant)
    grouped_menu = defaultdict(list)
    for item in menu_items:
        grouped_menu[item.category.name if item.category else "Uncategorized"].append(item)

    return render(request, 'add_menu.html', {
        'form': form,
        'restaurant': restaurant,
        'menu_items': menu_items,
        'grouped_menu': dict(grouped_menu),
        'is_partner': True,
    })

def delete_menu_item(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    if request.session.get('partner_logged_in') and item.restaurant.phone == request.session.get('partner_phone'):
        item.delete()
        messages.success(request, "✅ Item deleted successfully!")
    else:
        messages.error(request, "❌ Not authorized.")
    return redirect('add_menu', restaurant_id=item.restaurant.id)

def add_category(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    if not request.session.get('partner_logged_in') or restaurant.phone != request.session.get('partner_phone'):
        return redirect('partner_login')

    if request.method == 'POST':
        form = CategoryItem(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Category added successfully!")
            return redirect('add_menu', restaurant_id=restaurant.id)
    else:
        form = CategoryItem()

    return render(request, 'add_category.html', {'form': form, 'restaurant': restaurant})

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Email',
        'class': 'form-control'
    }))

def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if User.objects.filter(email=email).exists():
                # Save email in session to access in set_new_password
                request.session['reset_email'] = email
                return redirect('set_new_password')
            else:
                messages.error(request, "Email is not registered. Please sign up.")
    else:
        form = ForgotPasswordForm()
    return render(request, 'forgot_password.html', {'form': form})

class SetNewPasswordForm(forms.Form):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}),
        label='',
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'}),
        label='',
    )

from django.contrib.auth.forms import SetPasswordForm

def set_new_password(request):
    if request.method == 'POST':
        form = SetPasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password1']
            old_password = request.user.password

            if request.user.check_password(new_password):
                form.add_error('new_password1', 'New password must be different from old password.')
            else:
                form.save()
                messages.success(request, 'Password changed successfully. Please login.')
                return redirect('login')  # 👈 redirect to login
    else:
        form = SetPasswordForm(user=request.user)

    return render(request, 'set_new_password.html', {'form': form})

def add_to_cart(request):
    if request.method == "POST":
        item_id = str(request.POST.get("item_id"))
        quantity = int(request.POST.get("quantity", 1))

        cart = request.session.get('cart', {})
        cart[item_id] = cart.get(item_id, 0) + quantity

        request.session['cart'] = cart
        return redirect(request.META.get('HTTP_REFERER', 'view_cart'))

def remove_from_cart(request, item_id):
    cart = request.session.get('cart', {})
    item_id = str(item_id)

    if item_id in cart:
        if cart[item_id] > 1:
            cart[item_id] -= 1
        else:
            del cart[item_id]
        request.session['cart'] = cart

    return redirect(request.META.get('HTTP_REFERER', 'view_cart'))

from decimal import Decimal

# def view_cart(request):
#     cart = request.session.get('cart', {})
#     items = []
#     total_price = Decimal('0.00')

#     for item_id, qty in cart.items():
#         item = get_object_or_404(MenuItem, id=item_id)
#         item.quantity = qty
#         item.total_price = item.price * qty
#         items.append(item)
#         total_price += item.total_price

#     return render(request, 'cart.html', {'items': items, 'total_price': total_price})

def get_cart(request):
    return request.session.get('cart', {})

def save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True

# views.py
from collections import defaultdict
from .models import MenuItem

def view_cart(request):
    cart = get_cart(request)
    grouped_cart = defaultdict(list)
    total = 0

    for item_id, qty in cart.items():
        try:
            menu_item = MenuItem.objects.select_related('restaurant').get(id=item_id)
            subtotal = menu_item.price * qty
            total += subtotal
            grouped_cart[menu_item.restaurant].append({
                'menu_item': menu_item,
                'quantity': qty,
                'subtotal': subtotal
            })
        except MenuItem.DoesNotExist:
            pass

    return render(request, 'cart.html', {
        'grouped_cart': grouped_cart.items(),
        'total': total,
        'cart_count': sum(cart.values())
    })


# def remove_from_cart(request, item_id):
#     cart = get_cart(request)
#     item_id = str(item_id)
#     if item_id in cart:
#         del cart[item_id]
#         save_cart(request, cart)
#     return redirect('view_cart')

def clear_cart(request):
    request.session['cart'] = {}  # clear it
    request.session.modified = True
    return redirect('menu', restaurant_id=request.session.get('last_restaurant_id', 1))  # fallback to ID 1

from django.http import JsonResponse
import json

def update_cart_ajax(request):
    if request.method == "POST":
        data = json.loads(request.body)
        item_id = str(data.get("item_id"))
        action = data.get("action")

        cart = request.session.get('cart', {})
        qty = cart.get(item_id, 0)

        if action == "add":
            cart[item_id] = 1
        elif action == "increase":
            cart[item_id] = qty + 1
        elif action == "decrease":
            if qty > 1:
                cart[item_id] = qty - 1
            else:
                cart.pop(item_id, None)

        request.session['cart'] = cart
        return JsonResponse({
            "qty": cart.get(item_id, 0),
            "cart_count": sum(cart.values())
        })

def all_menus_by_restaurant(request):
    restaurants = Restaurant.objects.prefetch_related('menuitem_set').all()
    return render(request, 'all_menus.html', {'restaurants': restaurants})