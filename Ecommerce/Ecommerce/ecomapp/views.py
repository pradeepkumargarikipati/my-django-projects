from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from ecomapp.models import Product, Category, Order
from ecomapp.serializer import (
    ProductSerializer, CategorySerializer, OrderSerializer, 
    RegisterSerializer, UserProfileSerializer, CartSerializer
)

# -----------------------------------
# Product, Category, and Order Views
# -----------------------------------

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

# -----------------------------------
# Session-Based Cart Views
# -----------------------------------

class CartView(generics.GenericAPIView):
    """
    Retrieve the session-based cart.
    """
    def get(self, request):
        cart = request.session.get('cart', {})
        cart_items = [{'product_id': int(pid), 'quantity': qty} for pid, qty in cart.items()]
        serializer = CartSerializer(cart_items, many=True)
        return Response({'cart': serializer.data})

class AddToCartView(generics.GenericAPIView):
    """
    Add a product to the session-based cart.
    """
    def post(self, request):
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            session = request.session
            cart = session.get('cart', {})

            product_id = str(serializer.validated_data['product_id'])
            quantity = serializer.validated_data['quantity']

            if product_id in cart:
                cart[product_id] += quantity
            else:
                cart[product_id] = quantity

            session['cart'] = cart
            session.modified = True
            return Response({'cart': cart, 'message': 'Item added to cart'})

        return Response(serializer.errors, status=400)

class RemoveFromCartView(generics.GenericAPIView):
    """
    Remove a product from the session-based cart.
    """
    def post(self, request):
        session = request.session
        cart = session.get('cart', {})

        product_id = str(request.data.get('product_id'))
        if product_id in cart:
            del cart[product_id]
            session['cart'] = cart
            session.modified = True
            return Response({'cart': cart, 'message': 'Item removed from cart'})
        
        return Response({'error': 'Item not found in cart'}, status=404)

class ClearCartView(generics.GenericAPIView):
    """
    Clear the entire session-based cart.
    """
    def post(self, request):
        request.session['cart'] = {}
        request.session.modified = True
        return Response({'message': 'Cart cleared'})

# -----------------------------------
# Authentication Views
# -----------------------------------

class RegisterView(generics.CreateAPIView):
    """
    Register a new user.
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class LoginView(generics.GenericAPIView):
    """
    Login a user and return JWT tokens.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        user = authenticate(username=request.data['username'], password=request.data['password'])
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({'refresh': str(refresh), 'access': str(refresh.access_token)})
        return Response({'error': 'Invalid Credentials'}, status=400)

class LogoutView(generics.GenericAPIView):
    """
    Logout a user (handled client-side).
    """
    def post(self, request):
        return Response({'message': 'Logged out successfully'})

class UserProfileView(generics.RetrieveAPIView):
    """
    Retrieve the authenticated user's profile.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
