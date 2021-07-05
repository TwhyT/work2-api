from django.contrib import admin
from .models import Category, Product, ProductImage, Cart

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_enable']
    list_filter = ['is_enable']
    search_fields = ['name']

class ProductImageStackedInline(admin.StackedInline):
    model = ProductImage

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_enable']
    list_filter = ['is_enable']
    search_fields = ['name']
    inlines = [ ProductImageStackedInline ]

class CartAdmin(admin.ModelAdmin):
    list_display = ['id','user']



admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Cart, CartAdmin)
# admin.site.register(Invoice)
# admin.site.register(Invoice_Item)
