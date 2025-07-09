# """
# URL configuration for foodie project.

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/5.2/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """
# from django.contrib import admin
# from django.urls import path, reverse_lazy
# from django.conf.urls.static import static
# from django.conf import settings

# from foodieapp.views import staticWebsite, restaurant_list, menu_view, partner_login, verify_otp, city_not_found, partner_send_otp, partner_verify_otp, add_restaurant, enter_city, delete_restaurant, add_menu, delete_menu_item, add_category, forgot_password, set_new_password
# from foodieapp.views import signup, login_view

# from django.contrib.auth import views as auth_views
# # from foodieapp.forms import CustomPasswordResetForm, SetPasswordForm

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path("", staticWebsite, name="staticWebsite"),
#     path('<int:city_id>/', restaurant_list, name='restaurant_list'),
#     path('menu/<int:restaurant_id>/', menu_view, name='menu'),
#     # path('search-cities/', search_cities_ajax, name='search_cities_ajax'),
#     # path('restaurants/<int:city_id>/', city_restaurants, name='city_restaurants'),
#     path('signup', signup, name='signup'),
#     # path('dummyform', dummyform, name='dummyform')
#     path('login', login_view, name='login'),
#     path('forgot-password/', forgot_password, name='forgot_password'),
#     path('set-new-password/', set_new_password, name='set_new_password'),
#     path('partner/', partner_login, name='partner_login'),
#     path('verify-otp/', verify_otp, name='verify_otp'),
#     path('city-not-found/', city_not_found, name='city_not_found'),
#     path('partner/login/', partner_send_otp, name='partner_send_otp'),
#     path('partner/verify/', partner_verify_otp, name='partner_verify_otp'),
#     path('add-restaurant/', add_restaurant, name='add_restaurant'),
#     path('enter-city/', enter_city, name='enter_city'),
#     path('delete-restaurant/<int:restaurant_id>/', delete_restaurant, name='delete_restaurant'),
#     path('restaurant/<int:restaurant_id>/add-menu/', add_menu, name='add_menu'),
#     path('menu/delete/<int:item_id>/', delete_menu_item, name='delete_menu_item'),
#     path('restaurant/<int:restaurant_id>/add-category/', add_category, name='add_category'),
#     path('<str:city_name>/', restaurant_list, name='restaurant_list'),

# ]
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from foodieapp.views import (
    staticWebsite, restaurant_list, menu_view, partner_login, verify_otp,
    city_not_found, partner_send_otp, partner_verify_otp, add_restaurant,
    enter_city, delete_restaurant, add_menu, delete_menu_item, add_category,
    forgot_password, set_new_password, signup, login_view, add_to_cart, view_cart,
    remove_from_cart, clear_cart, update_cart_ajax, all_menus_by_restaurant
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', staticWebsite, name='staticWebsite'),
    
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),

    path('forgot-password/', forgot_password, name='forgot_password'),
    path('set-new-password/', set_new_password, name='set_new_password'),

    path('partner/', partner_login, name='partner_login'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('partner/login/', partner_send_otp, name='partner_send_otp'),
    path('partner/verify/', partner_verify_otp, name='partner_verify_otp'),

    path('city-not-found/', city_not_found, name='city_not_found'),

    path('add-restaurant/', add_restaurant, name='add_restaurant'),
    path('enter-city/', enter_city, name='enter_city'),
    path('delete-restaurant/<int:restaurant_id>/', delete_restaurant, name='delete_restaurant'),

    path('restaurant/<int:restaurant_id>/add-menu/', add_menu, name='add_menu'),
    path('menu/<int:restaurant_id>/', menu_view, name='menu'),
    path('menu/delete/<int:item_id>/', delete_menu_item, name='delete_menu_item'),

    path('restaurant/<int:restaurant_id>/add-category/', add_category, name='add_category'),

    path('add-to-cart/<int:item_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='view_cart'),
    
    path('cart/', view_cart, name='view_cart'),
    path('cart/add/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', clear_cart, name='clear_cart'),
    path('update-cart/', update_cart_ajax, name='update_cart_ajax'),
    path('all-menus/', all_menus_by_restaurant, name='all_menus'),



    # ⚠ Order matters: int pattern should be before str
    path('<int:city_id>/', restaurant_list, name='restaurant_list'),
    path('<str:city_name>/', restaurant_list, name='restaurant_list'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
