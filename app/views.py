from rest_framework import viewsets, status, filters, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    CustomerProfile, Wallet, BankCard, Transaction,
    PaymentCategory, ServiceProvider, Payment,
    FavoritePayment, Notification
)
from .serializers import (
    CustomerProfileSerializer, WalletSerializer, BankCardSerializer,
    TransactionSerializer, PaymentCategorySerializer, ServiceProviderSerializer,
    PaymentSerializer, FavoritePaymentSerializer, NotificationSerializer,
    TopUpSerializer, TransferSerializer
)

# 1. FBV барои PaymentCategory (Мувофиқи Day 1)
@api_view(['GET', 'POST'])
def payment_category_list(request):
    if request.method == 'GET':
        categories = PaymentCategory.objects.all()
        serializer = PaymentCategorySerializer(categories, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = PaymentCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PATCH', 'DELETE'])
def payment_category_detail(request, pk):
    try:
        category = PaymentCategory.objects.get(pk=pk)
    except PaymentCategory.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PaymentCategorySerializer(category)
        return Response(serializer.data)
    elif request.method == 'PATCH':
        serializer = PaymentCategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# 2. ViewSets барои CRUD-и стандартӣ (Day 3)
class CustomerProfileViewSet(viewsets.ModelViewSet):
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer

class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'currency']

class BankCardViewSet(viewsets.ModelViewSet):
    queryset = BankCard.objects.all()
    serializer_class = BankCardSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['masked_pan', 'card_holder']

class ServiceProviderViewSet(viewsets.ModelViewSet):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name']

class FavoritePaymentViewSet(viewsets.ModelViewSet):
    queryset = FavoritePayment.objects.all()
    serializer_class = FavoritePaymentSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

# 3. APIView барои Logic-и махсус (TopUp ва Transfer)
class TopUpAPIView(APIView):
    serializer_class = TopUpSerializer  
    def post(self, request):
        serializer = TopUpSerializer(data=request.data)
        if serializer.is_valid():
            wallet_id = serializer.validated_data['wallet_id']
            amount = serializer.validated_data['amount']
            
            with transaction.atomic():
                wallet = Wallet.objects.select_for_update().get(pk=wallet_id)
                wallet.balance += amount
                wallet.save()

                new_trans = Transaction.objects.create(
                    receiver_wallet=wallet,
                    transaction_type='TOP_UP',
                    amount=amount,
                    total_amount=amount,
                    currency=wallet.currency,
                    status='SUCCESS',
                    description=serializer.validated_data.get('description', '')
                )
                return Response(TransactionSerializer(new_trans).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TransferAPIView(APIView):
    serializer_class = TransferSerializer
    def post(self, request):
        serializer = TransferSerializer(data=request.data)
        if serializer.is_valid():
            s_id = serializer.validated_data['sender_wallet_id']
            r_num = serializer.validated_data['receiver_wallet_number']
            amount = serializer.validated_data['amount']

            with transaction.atomic():
                sender = Wallet.objects.select_for_update().get(pk=s_id)
                receiver = Wallet.objects.select_for_update().get(wallet_number=r_num)

                if sender.balance < amount:
                    return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

                sender.balance -= amount
                receiver.balance += amount
                sender.save()
                receiver.save()

                new_trans = Transaction.objects.create(
                    sender_wallet=sender,
                    receiver_wallet=receiver,
                    transaction_type='TRANSFER',
                    amount=amount,
                    total_amount=amount,
                    currency=sender.currency,
                    status='SUCCESS',
                    description=serializer.validated_data.get('description', '')
                )
                return Response(TransactionSerializer(new_trans).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 4. GenericAPIView барои Payments ва Transactions List
class TransactionListAPIView(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'transaction_type']
    search_fields = ['description']

class PaymentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def perform_create(self, serializer):
        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(pk=self.request.data['wallet_id'])
            amount = serializer.validated_data['amount']
            
            wallet.balance -= amount
            wallet.save()
            
            trans = Transaction.objects.create(
                sender_wallet=wallet,
                transaction_type='PAYMENT',
                amount=amount,
                total_amount=amount,
                currency=wallet.currency,
                status='SUCCESS'
            )
            serializer.save(transaction=trans, status='SUCCESS')

# 5. Нотификатсияро хондашуда кардан
class MarkNotificationReadAPIView(APIView):
    def patch(self, request, pk):
        try:
            notif = Notification.objects.get(pk=pk)
            notif.is_read = True
            notif.save()
            return Response({'status': 'marked as read'})
        except Notification.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)