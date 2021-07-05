from django.contrib.auth.models import User
from django.core.checks.messages import Error
from rest_framework import response, serializers, status
from rest_framework.exceptions import AuthenticationFailed, NotFound, ParseError, ValidationError
from .models import Cart, Category, User, Product, ProductImage
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

#Token System
class MyTokenRefreshLifetimeSerializer(TokenRefreshSerializer):

    def validate(self, attrs):
        try:
            data = super().validate(attrs)
            data['token_type'] = str(RefreshToken.token_type)
            data['expire_in'] = int(RefreshToken.lifetime.total_seconds())
            return data
        except:
            raise ValidationError({'msg' : 'Refetch token ไม่ถูกต้อง', 'code': 'REFETCH_TOKEN_FAIL'}, 400)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        try:
            data = super().validate(attrs)
            token = self.get_token(self.user)
            data['token_type'] = str(AccessToken.token_type)
            data['expire_in'] = int(token.access_token.lifetime.total_seconds())
            return data
        except:
            raise ValidationError({'msg':'ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง', "CODE":"LOGIN_FAIL"}, status.HTTP_400_BAD_REQUEST)

class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length = 100, error_messages={'blank':'กรุณากรอกชื่อผู้ใช้งาน'})
    password = serializers.CharField(error_messages={'blank':'กรุณากรอกรหัสผ่าน'})
    password2 = serializers.CharField()
    User
    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'first_name', 'last_name')
        extra_kwargs = {
            'password':{'write_only': True},
            'password2':{'write_only': True},
        } 
    User

    def validate_password(self, password):
        password2 = self.initial_data['password2'] 
        # if User.objects.filter(username = data['username']):
        #     raise ValidationError({'username':'มีผู้ใช้งาน username นี้แล้ว',}, status.HTTP_400_BAD_REQUEST)
        
        if len(password) < 8:
            raise ValidationError({'password':'กรุณาใส่ password มากกว่า 8 ตัว'}, status.HTTP_400_BAD_REQUEST)
        
        if password == password2:
            raise ValidationError({'password':'password ไม่ตรงกัน'}, status.HTTP_400_BAD_REQUEST)
        return password

    def create(self, validated_data):
        user = User.objects.create_user(username = validated_data['username'],
                                        password = validated_data['password'],
                                        first_name = validated_data['first_name'],
                                        last_name = validated_data['last_name'])
        user.save()
        return user

# Category
class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('url', 'id', 'name', 'image', 'is_enable')

class CategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'detail', 'image', 'is_enable')

#Product

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image')

class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('url', 'id', 'name', 'price', 'image', 'is_enable')

class ProductDetailSerializer(serializers.ModelSerializer):
    album = ProductImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ('url', 'id', 'name', 'price', 'detail', 'image', 'album', 'is_enable')

#Cart
class CartListSerializer(serializers.ModelSerializer):
    product = serializers.CharField(max_length = 100, error_messages={'blank':'กรุณาใส่ข้อความ'})
    quantity = serializers.CharField(error_messages={'blank':'กรุณาใส่จำนวน'})
    class Meta:
        model = Cart
        fields = ('id', 'product', 'user', 'quantity', 'total')
        owner = serializers.ReadOnlyField(source='owner.username')

    def validate_product(self, product):
        
        if Product.objects.filter(pk=product):
            product_is = Product.objects.filter(pk=product)
            if product_is.filter(is_enable = False):
                raise ValidationError('สินค้านี้ถูกปิดใช้งาน')
            return product
        else:
            raise ValidationError('ไม่พบสินค้านี้')

    def validate_quantity(self, quantity):
        if int(quantity) < 1:
            raise ValidationError({'quantity':'จำนวนสินค้าต้องมากกว่า 0'})
        return quantity
           
class CartDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cart
        fields = ('id', 'product', 'user', 'quantity', 'total')
        owner = serializers.ReadOnlyField(source='owner.user')



class CheckoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = fields = ('id', 'product', 'user', 'quantity', 'total')
        owner = serializers.ReadOnlyField(source='owner.user')

class InvoiceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = fields = ('id', 'product', 'user', 'quantity', 'total')
        owner = serializers.ReadOnlyField(source='owner.user')
