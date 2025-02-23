from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Transaction

class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "username", "email", "is_staff"]

class HistoricalTransactionSerializer(serializers.ModelSerializer):
    history_user = SimpleUserSerializer(read_only=True)
    class Meta:
        model = Transaction.history.model
        fields = ["id", "merchant", "amount", "status", "approved_by", "is_flagged", 
                  "history_date", "history_user", "history_type"]

class TransactionSerializer(serializers.ModelSerializer):
    approved_by = SimpleUserSerializer(read_only=True)
    history = HistoricalTransactionSerializer(many=True, read_only=True, source="history.all")
    class Meta:
        model = Transaction
        fields = ["id", "merchant", "amount", "status", "approved_by", "is_flagged", "history"]