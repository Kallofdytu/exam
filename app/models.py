from django.db import models
from django.contrib.auth.models import User

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20)
    birth_date = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    passport_number = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.phone_number}"

class Wallet(models.Model):
    CURRENCY_CHOICES = [
        ('TJS', 'TJS'),
        ('USD', 'USD'),
        ('RUB', 'RUB'),
    ]
    STATUS_CHOICES = [
        ('ACTIVE', 'ACTIVE'),
        ('BLOCKED', 'BLOCKED'),
        ('CLOSED', 'CLOSED'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    wallet_number = models.CharField(max_length=20, unique=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='TJS')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.wallet_number}) - {self.balance} {self.currency}"

class BankCard(models.Model):
    CARD_TYPES = [
        ('VISA', 'VISA'),
        ('MASTERCARD', 'MASTERCARD'),
        ('KORTI_MILLI', 'KORTI MILLI'),
        ('OTHER', 'OTHER'),
    ]
    STATUS_CHOICES = [
        ('ACTIVE', 'ACTIVE'),
        ('BLOCKED', 'BLOCKED'),
        ('EXPIRED', 'EXPIRED'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cards')
    card_holder = models.CharField(max_length=100)
    masked_pan = models.CharField(max_length=25)
    card_type = models.CharField(max_length=20, choices=CARD_TYPES)
    expire_month = models.IntegerField()
    expire_year = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.card_type} - {self.masked_pan}"

class PaymentCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ServiceProvider(models.Model):
    category = models.ForeignKey(PaymentCategory, on_delete=models.CASCADE, related_name='providers')
    name = models.CharField(max_length=100)
    account_mask = models.CharField(max_length=50)
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)
    commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    TYPE_CHOICES = [
        ('TOP_UP', 'TOP_UP'),
        ('TRANSFER', 'TRANSFER'),
        ('PAYMENT', 'PAYMENT'),
        ('WITHDRAW', 'WITHDRAW'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'PENDING'),
        ('SUCCESS', 'SUCCESS'),
        ('FAILED', 'FAILED'),
        ('CANCELLED', 'CANCELLED'),
    ]

    sender_wallet = models.ForeignKey(Wallet, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_transactions')
    receiver_wallet = models.ForeignKey(Wallet, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_transactions')
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='TJS')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} ({self.status})"

class Payment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'PENDING'),
        ('SUCCESS', 'SUCCESS'),
        ('FAILED', 'FAILED'),
        ('CANCELLED', 'CANCELLED'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='payments')
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='payments')
    account_number = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission = models.DecimalField(max_digits=12, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    transaction = models.OneToOneField(Transaction, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment to {self.provider.name} - {self.amount}"

class FavoritePayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Notification(models.Model):
    TYPE_CHOICES = [
        ('TRANSACTION', 'TRANSACTION'),
        ('PAYMENT', 'PAYMENT'),
        ('SYSTEM', 'SYSTEM'),
        ('CARD', 'CARD'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title