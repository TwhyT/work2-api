from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.db.models.fields import BooleanField, CharField, TextField
from django.db.models.fields.files import ImageField
from django.db.models.fields.related import ForeignKey
from django.core.validators import MinValueValidator

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField( upload_to='upload/category', null=True, blank=True)
    detail = models.TextField(max_length=255)
    is_enable = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #     return reversed("categorydetail", kwargs={"pk": self.pk})
    

class Product(models.Model):
    category = models.ForeignKey(Category, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    detail = models.TextField(max_length=255)
    image = models.ImageField( upload_to='upload/product', null=True, blank=True)
    is_enable = models.BooleanField(default=True)
    created_datetime = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name = 'album',on_delete = models.CASCADE)
    image = models.ImageField(upload_to='upload/product', null=True, blank=True)

    class Meta:
        verbose_name = 'img'
        verbose_name_plural = 'img'

class Cart(models.Model):
    product = models.ForeignKey(Product, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    def __str__(self):
        return str('Owner '+self.user.username)

CHOICE_STATUS = (
    ('Wait', 'Wait for delivery'),
    ('Delivery', 'Delivery'),
    ('Cancel', 'Cancel'),
)

class Invoice(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    created_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now=True)
    total = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, null=True, blank=False, choices=CHOICE_STATUS)

    def __str__(self):
        return str(self.user.username)

# class Invoice_Item(models.Model):
#     product = models.ForeignKey(Product, null=True, on_delete=models.CASCADE)
#     invoice = models.ForeignKey(Invoice, null=True, on_delete=models.CASCADE)
#     created_datetime = models.DateTimeField(auto_now_add=True)
#     quantity = models.PositiveIntegerField(default=0)
#     total = models.PositiveIntegerField(default=0)

#     def __str__(self):
#         return str(self.invoice.user.username)