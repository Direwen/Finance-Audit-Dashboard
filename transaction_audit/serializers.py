from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Transaction

class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "username", "email", "is_staff"]

class TransactionSerializer(serializers.ModelSerializer):
    approved_by = SimpleUserSerializer(read_only=True)
    
    class Meta:
        model = Transaction
        fields = ["id", "merchant", "amount", "status", "approved_by", "is_flagged"]