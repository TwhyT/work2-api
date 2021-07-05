
from django.conf.urls import url
from django.contrib.auth.models import Permission, User
from django.http import request
from django.utils.encoding import filepath_to_uri
import django_filters
from django_filters.filters import LookupChoiceFilter
from rest_framework import filters
from rest_framework import serializers
from rest_framework import response
from rest_framework.serializers import Serializer
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from .models import Cart, Category, Invoice, Product
from django.shortcuts import render
from .serializers import CartDetailSerializer, CartListSerializer, CategoryDetailSerializer, CategoryListSerializer, InvoiceListSerializer, MyTokenObtainPairSerializer, CartListSerializer, ProductDetailSerializer, ProductListSerializer, RegisterSerializer
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView
from .serializers import MyTokenRefreshLifetimeSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import AuthenticationFailed, NotFound, ParseError, ValidationError
from rest_framework import permissions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication



# Create your views here.
class CustomResultsSetPagination(PageNumberPagination):
    page = 1
    page_query_param = 'page'
    page_size = 10
    page_size_query_param = 'page_size'
    
    def get_paginated_response(self, data):
        return Response({
            'results': data,
            'next': str(self.get_next_link()),
            'previous': str(self.get_previous_link()),
            'count': int(self.page.paginator.count),
            'limit': self.page_size,
        })

#User System
class RefreshView(TokenRefreshView):
    serializer_class = MyTokenRefreshLifetimeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except:
            raise ParseError(serializer.errors)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class AccessView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except:
            raise ParseError(serializer.errors)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class RegisterApi(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
    
    def post(self, request, *args,  **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'token_type' : str(AccessToken.token_type),
                'expire_in' : int(AccessToken.lifetime.total_seconds()),
            })
        else:
            raise ParseError({
                 'msg' : 'ลงทะเบียนไม่สำเร็จ',
                 'code': 'REGISTER_FAIL',
                 'errors':serializer.errors,
            })

#Category
class ResponseInfoCategory(object):
    def __init__(self, user=None, **args):
        self.response = {
            "msg": args.get('msg', 'ดึงข้อมูลสำเร็จ'),
            "data": args.get('data', []),
        }

class CategoryList(generics.ListAPIView):
    
    queryset = Category.objects.all()
    serializer_class = CategoryListSerializer
    pagination_class = CustomResultsSetPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    filterset_fields = ['is_enable']
    
    def __init__(self, **kwargs):
        self.response_format = ResponseInfoCategory().response
        super(CategoryList, self).__init__(**kwargs)

    def list(self, request, *args, **kwargs):
        response_data = super(CategoryList, self).list(request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        return Response(self.response_format)

class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryDetailSerializer
    filter_backends = [DjangoFilterBackend]

    def __init__(self, **kwargs):
        self.response_format = ResponseInfoCategory().response
        super(CategoryDetail, self).__init__(**kwargs)

    def retrieve(self, request, *args, **kwargs):
        try:
            response_data = super(CategoryDetail, self).retrieve(request, *args, **kwargs)
            self.response_format["data"] = response_data.data
            return Response(self.response_format)
        except:
            raise NotFound({'code':'HTTP_404_NOT_FOUND',
                                    'msg': 'ไม่พบข้อมูล'}, 
                                    status.HTTP_404_NOT_FOUND)
 
#Product
class ResponseInfoProduct(object):
    def __init__(self, user=None, **args):
        self.response = {
            "msg": args.get('msg', 'ดึงข้อมูลสำเร็จ'),
            "data": args.get('data', []),
        }

class ProductList(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer
    pagination_class = CustomResultsSetPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    filterset_fields = ['is_enable',]
    search_fields = ['name', 'detail']
    ordering_fields = ['quantity','total']

    def get_queryset(self):
        queryset = Product.objects.all()
        search = self.request.query_params.get('search')
        sort_price_by = self.request.query_params.get('sort_price')
        sort_date_by = self.request.query_params.get('sort_date')
        category_in = self.request.query_params.get('category__in',None)
        category_not_in = self.request.query_params.get('category_not_in',None)

        categoryIn =[]
        categoryNotin =[]

        if search:
            queryset = queryset.filter(name__contains = search, 
                                        # detail__contains = search
                                        )

        if category_in:
            for i in category_in.split(","):
                categoryIn.append(int(i))

        if category_not_in:
            for i in category_not_in.split(","):
                categoryIn.append(int(i))
        
        if category_in:
            queryset = queryset.filter(category__in=categoryIn)
        if category_not_in:
            queryset = queryset.exclude(category__in=categoryNotin)
        
        if sort_price_by == 'asc':
            queryset = queryset.order_by('price')
        elif sort_price_by == 'desc':
            queryset = queryset.order_by('-price')
        
        if sort_date_by == 'asc':
            queryset = queryset.order_by('created_datetime')
        elif sort_date_by == 'desc':
            queryset = queryset.order_by('-created_datetime')

        return queryset

    def __init__(self, **kwargs):
        self.response_format = ResponseInfoProduct().response
        super(ProductList, self).__init__(**kwargs)

    def list(self, request, *args, **kwargs):
        response_data = super(ProductList, self).list(request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        return Response(self.response_format)

class ProductDetail(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    filter_backends = [DjangoFilterBackend]

    def __init__(self, **kwargs):
        self.response_format = ResponseInfoProduct().response
        super(ProductDetail, self).__init__(**kwargs)

    def retrieve(self, request, *args, **kwargs):
        try:
            response_data = super(ProductDetail, self).retrieve(request, *args, **kwargs)
            self.response_format["data"] = response_data.data
            return Response(self.response_format)
        except:
            raise NotFound({'code':'HTTP_404_NOT_FOUND',
                                    'msg': 'ไม่พบข้อมูล'}, 
                                    status.HTTP_404_NOT_FOUND)

#Cart
class ResponseInfoCart(object):
    def __init__(self, user=None, **args):
        self.response = {
            "msg": args.get('msg', 'ดึงข้อมูลสำเร็จ'),
            "data": args.get('data', []),
        }

class CartList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Cart.objects.all()
    serializer_class = CartListSerializer
    pagination_class = CustomResultsSetPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    filterset_fields = ['product']
    ordering_fields = ['quantity','total']

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        data = {}
        print(serializer.is_valid())
        if serializer.is_valid():
            user_id = self.request.user
            user = User.objects.get(username=user_id)
            product_id = serializer.data['product']
            products = Product.objects.get(id=int(product_id))
            quantities = int(serializer.data['quantity'])
            item = Cart.objects.filter(user=user,product=products.id).first()
            if item:
                item.quantity = item.quantity + quantities
                calculate = quantities*products.price
                item.total = item.total + calculate
                item.save()
            else:
                item = Cart.objects.create(product=products,user=user,quantity=quantities,total=quantities*products.price)
                item.save()
                item = Cart.objects.filter(user=user)

            data['id'] = int(item.id)
            data['product'] = str(item.product)
            data['quantity'] = int(item.quantity)
            data['total'] = item.total
            return Response({"data": data,
                            "msg":"บันทึกสำเร็จ"},status.HTTP_201_CREATED)
        else:
            return Response({
                "code" : "ADD_TO_CART_FAIL",
                "msg" : "บันทึกไม่สำเร็จ",
                "error" : [serializer.errors]
            },status=status.HTTP_400_BAD_REQUEST)

    def __init__(self, **kwargs):
        self.response_format = ResponseInfoCart().response
        super(CartList, self).__init__(**kwargs)

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            response_data = super(CartList, self).list(request, *args, **kwargs)
            self.response_format["data"] = response_data.data
            return Response(self.response_format)
        except:
            return AuthenticationFailed()

class CartDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Cart.objects.all()
    serializer_class = CartDetailSerializer

    def update(self, request, pk):
        try:
            cartlist = Cart.objects.get(id=pk)
            data = request.data
            cartlist.total = int(data['quantity'])*(cartlist.product.price)
            cartlist.quantity = data['quantity']

            if int(cartlist.quantity) == 0 :
                cartlist.delete()
                cartlist.save()
                return Response({'msg':'ลบสำเร็จ'})
            
            else:
                cartlist.save()
                return Response(CartDetailSerializer(cartlist).data)
        except:
            raise NotFound()

    
# class CartDetail(generics.DestroyAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     queryset = Cart.objects.all()
#     serializer_class = CartDetailSerializer
    
    def delete(self, request, pk):
        try:
            cartlist = Cart.objects.get(id=pk)
            cartlist.delete()
            cartlist.save()
            return Response({'msg':'ลบสำเร็จ'})
        except:
            raise NotFound()

class CheckOut(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Cart.objects.all()
    serializer_class = InvoiceListSerializer

    def create(self, request, *args, **kwargs):
        order_user = self.request.user
        return super().create(request, *args, **kwargs)


class InvoiceList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Invoice.objects.all()
    serializer_class = InvoiceListSerializer

    # def list(self, request, *args, **kwargs):
    #     order_user = self.request.user
    #     queryset = Cart.objects.filter(user=order_user)
        
    #     list_invoice = []
    #     sum=0
    #     for item in queryset:
    #         sum += item.total
    #         list_invoice.append(str(item)+" : "+str(item.quantity) + " X " + str(item.product.price) + " = " + str(item.total) + "บาท")
    #         my_invoice = list_invoice
    #     invoices = Invoice.objects.create(user=order_user,total=sum)
    #     invoices.save()
    #     return Response({
    #         "msg": "ดึงข้อมูลสำเร็จ",
    #         "data" : ({
    #             "invoice" : str(order_user.id),
    #             "list invoice" : my_invoice,
    #             "total" : str(sum) + " บาท"
    #             })
    #     })