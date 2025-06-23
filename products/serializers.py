from rest_framework import serializers
from .models import CartItem,Item
from django.contrib.auth import get_user_model
User = get_user_model()


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
      
        fields = ['id', 'title', 'description', 'owner', 'created_at']
        read_only_fields = ['owner', 'created_at']

class CartItemSerializer(serializers.ModelSerializer):
    item_title = serializers.ReadOnlyField(source='item.title')

    class Meta:
        model = CartItem
        fields = ['id', 'item', 'item_title', 'quantity', 'added_at']
        read_only_fields = ['added_at']
