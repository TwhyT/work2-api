from django.contrib import admin
from django.urls import path, include
from . import views
from .views import RefreshView, AccessView, RegisterApi


# from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView,)

urlpatterns = [
    path('api-auth', include('rest_framework.urls', namespace='rest_framework')),

    path('category/', views.CategoryList.as_view()),
    path('category/<slug:pk>/', views.CategoryDetail.as_view(), name='category-detail'),

    path('product/', views.ProductList.as_view()),
    path('product/<slug:pk>/', views.ProductDetail.as_view(), name='product-detail'),

    path('cart/', views.CartList.as_view()),
    path('cart/<slug:pk>/', views.CartDetail.as_view(), name='cart-detail'),

    path('checkout/', views.InvoiceList.as_view()),
    path('invoice/', views.InvoiceList.as_view()),

    path('token/', AccessView.as_view()),
    path('token/refresh/', RefreshView.as_view()),
    path('register/', RegisterApi.as_view()),
]