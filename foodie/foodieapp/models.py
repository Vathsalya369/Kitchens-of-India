from django.db import models
from django.utils import timezone
from cloudinary.models import CloudinaryField

# Create your models here.

class City(models.Model):
    name=models.CharField(max_length=100)
    state=models.CharField(max_length=100, blank=True, null=True)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(default=timezone.now)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural="Cities"
        ordering=['name']        
    def __str__(self):
        return self.name

# restaurants in city
class Restaurant(models.Model):
    name=models.CharField(max_length=100)
    city=models.ForeignKey(City, on_delete=models.CASCADE)
    image=models.ImageField(upload_to="restaurants/")
    address=models.TextField()
    phone=models.CharField(max_length=15, blank=True, null=True)
    rating=models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    is_active=models.BooleanField(default=True)
    delivery_time=models.CharField(max_length=50, default="30-45 mins")
    created_at=models.DateTimeField(default=timezone.now)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.city.name}"

class Category(models.Model):
    name=models.CharField(max_length=50)
    icon = models.CharField(max_length=50, blank=True, null=True)  # Font Awesome icon class
    is_active = models.BooleanField(default=True)
    created_at=models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name
    
# menu items in restaurant
class MenuItem(models.Model):
    # category_choices=['Starters', 'Main Course', 'Dessert', 'Beverage', 'Rice and Biryani', 'Fried Rice', 'Breads', 'Deals of The Day', 'Snacks', 'Tandoori Starters', 'Soups', 'Salads']
    restaurant=models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    # category=models.CharField(max_length=20, choices=category_choices)
    category=models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    name=models.CharField(max_length=100)
    price=models.DecimalField(max_digits=6, decimal_places=2)
    # image=models.ImageField(upload_to="menu_items/", blank=True)
    image = CloudinaryField('image')
    description=models.TextField(blank=True)
    is_vegetarian = models.BooleanField(default=False)  # Veg/Non-veg indicator
    is_available = models.BooleanField(default=True)  # Availability
    is_popular = models.BooleanField(default=False)  # Popular items
    created_at=models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return self.name

class Partner(models.Model):
    phone = models.CharField(max_length=15, unique=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.phone