from django.contrib import admin

from .models import City, Restaurant, MenuItem, Category, Partner

# Register your models here.
class CityAdmin(admin.ModelAdmin):
    list_display=('name','state', 'is_active', 'created_at', 'updated_at')
admin.site.register(City, CityAdmin)

class RestaurantAdmin(admin.ModelAdmin):
    list_display=('name', 'city', 'image', 'address', 'phone', 'rating', 'is_active', 'delivery_time', 'created_at', 'updated_at')
admin.site.register(Restaurant, RestaurantAdmin)

class MenuItemAdmin(admin.ModelAdmin):
    list_display=('restaurant', 'category', 'name', 'price', 'image', 'description', 'is_vegetarian', 'is_available', 'is_popular', 'created_at', 'updated_at')
admin.site.register(MenuItem, MenuItemAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display=('name', 'icon', 'is_active', 'created_at')
admin.site.register(Category, CategoryAdmin)

class PartnerAdmin(admin.ModelAdmin):
    list_display = ('phone', 'joined_at')
    search_fields = ('phone',)
admin.site.register(Partner, PartnerAdmin)