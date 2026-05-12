from rest_framework import serializers
from django.contrib.auth.models import User
from datetime import date
from .models import (
    CustomerProfile, Wallet, BankCard, Transaction,
    PaymentCategory, ServiceProvider, Payment,
    FavoritePayment, Notification
)
import random

class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class CustomerProfileSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CustomerProfile
        fields = ['id', 'user', 'user_id', 'phone_number', 'birth_date', 'address', 'passport_number', 'created_at', 'updated_at']

    def validate_phone_number(self, value):
        if not value:
            raise serializers.ValidationError("Phone number cannot be empty.")
        return value


class WalletSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Wallet
        fields = ['id', 'user', 'user_id', 'wallet_number', 'balance', 'currency', 'status', 'created_at', 'updated_at']
        read_only_fields = ['balance', 'wallet_number', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Гирифтани user_id ва сохтани рақами тасодуфӣ
        uid = validated_data.pop('user_id')
        
        # Генератори рақами оддӣ (9-рақама)
        num = str(random.randint(100000000, 999999999))
        
        # Сохтани объект
        return Wallet.objects.create(user_id=uid, wallet_number=num, **validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['balance'] = f"{instance.balance} {instance.currency}"
        return data
class BankCardSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = BankCard
        fields = ['id', 'user', 'user_id', 'card_holder', 'masked_pan', 'card_type', 'expire_month', 'expire_year', 'status', 'created_at']

    def validate_expire_month(self, value):
        if value < 1 or value > 12:
            raise serializers.ValidationError("Expire month must be between 1 and 12.")
        return value

    def validate_expire_year(self, value):
        current_year = date.today().year
        if value < current_year:
            raise serializers.ValidationError("Expire year cannot be in the past.")
        return value

    def validate_masked_pan(self, value):
        if not value or len(value) < 16:
            raise serializers.ValidationError("Invalid masked PAN format.")
        return value

class PaymentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentCategory
        fields = ['id', 'name', 'description', 'is_active', 'created_at']

class ServiceProviderSerializer(serializers.ModelSerializer):
    category = PaymentCategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ServiceProvider
        fields = ['id', 'category', 'category_id', 'name', 'account_mask', 'min_amount', 'max_amount', 'commission_percent', 'is_active', 'created_at']

class WalletShortSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Wallet
        fields = ['wallet_number', 'owner']

class TransactionSerializer(serializers.ModelSerializer):
    sender_wallet = WalletShortSerializer(read_only=True)
    receiver_wallet = WalletShortSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'sender_wallet', 'receiver_wallet', 'transaction_type', 'amount', 'commission', 'total_amount', 'currency', 'status', 'description', 'created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        type_map = {
            'TOP_UP': 'Пур кардани ҳамён',
            'TRANSFER': 'Интиқоли пул',
            'PAYMENT': 'Пардохт',
            'WITHDRAW': 'Баровардани пул',
        }
        status_map = {
            'PENDING': 'Дар интизор',
            'SUCCESS': 'Иҷро шуд',
            'FAILED': 'Иҷро нашуд',
            'CANCELLED': 'Бекор шуд',
        }
        data['transaction_type'] = type_map.get(instance.transaction_type, instance.transaction_type)
        data['status'] = status_map.get(instance.status, instance.status)
        data['amount'] = f"{instance.amount} {instance.currency}"
        data['commission'] = f"{instance.commission} {instance.currency}"
        data['total_amount'] = f"{instance.total_amount} {instance.currency}"
        return data

class TopUpSerializer(serializers.Serializer):
    wallet_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    description = serializers.CharField(required=False, allow_blank=True)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value

class TransferSerializer(serializers.Serializer):
    sender_wallet_id = serializers.IntegerField()
    receiver_wallet_number = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    description = serializers.CharField(required=False, allow_blank=True)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value

class PaymentSerializer(serializers.ModelSerializer):
    provider = ServiceProviderSerializer(read_only=True)
    provider_id = serializers.IntegerField(write_only=True)
    user = UserShortSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    wallet = WalletShortSerializer(read_only=True)
    wallet_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'user', 'user_id', 'wallet', 'wallet_id', 'provider', 'provider_id', 'account_number', 'amount', 'commission', 'total_amount', 'status', 'created_at']
        read_only_fields = ['commission', 'total_amount', 'status']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        curr = instance.wallet.currency if instance.wallet else "TJS"
        data['amount'] = f"{instance.amount} {curr}"
        data['total_amount'] = f"{instance.total_amount} {curr}"
        return data

class FavoritePaymentSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    provider = ServiceProviderSerializer(read_only=True)
    provider_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = FavoritePayment
        fields = ['id', 'user', 'user_id', 'provider', 'provider_id', 'title', 'account_number', 'created_at']

class NotificationSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'user', 'title', 'message', 'notification_type', 'is_read', 'created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['status_text'] = 'Хонда шудааст' if instance.is_read else 'Хонда нашудааст'
        return data