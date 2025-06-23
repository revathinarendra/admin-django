from django.urls import path
from . import views

urlpatterns = [
    # Item CRUD
    path('items/', views.ItemListCreateView.as_view(), name='item-list-create'),
    path('items/<int:pk>/', views.ItemDetailView.as_view(), name='item-detail'),

    # CartItem CRUD
    path('cart-items/', views.CartItemListCreateView.as_view(), name='cartitem-list-create'),
    path('cart-items/<int:pk>/', views.CartItemDetailView.as_view(), name='cartitem-detail'),
]
