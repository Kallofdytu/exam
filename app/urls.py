from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomerProfileViewSet, WalletViewSet, BankCardViewSet,
    ServiceProviderViewSet, FavoritePaymentViewSet, NotificationViewSet,
    payment_category_list, payment_category_detail,
    TopUpAPIView, TransferAPIView, TransactionListAPIView,
    PaymentListCreateAPIView, MarkNotificationReadAPIView,
    RegisterAPIView, LoginAPIView
)

router = DefaultRouter()
router.register(r'profiles', CustomerProfileViewSet, basename='profile')
router.register(r'wallets', WalletViewSet, basename='wallet')
router.register(r'cards', BankCardViewSet, basename='card')
router.register(r'providers', ServiceProviderViewSet, basename='provider')
router.register(r'favorites', FavoritePaymentViewSet, basename='favorite')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),

    path('auth/register/', RegisterAPIView.as_view(), name='auth_register'),
    path('auth/login/', LoginAPIView.as_view(), name='auth_login'),

    path('payment-categories/', payment_category_list, name='category_list'),
    path('payment-categories/<int:pk>/', payment_category_detail, name='category_detail'),

    path('transactions/', TransactionListAPIView.as_view(), name='transaction_list'),
    path('transactions/top-up/', TopUpAPIView.as_view(), name='transaction_topup'),
    path('transactions/transfer/', TransferAPIView.as_view(), name='transaction_transfer'),

    path('payments/', PaymentListCreateAPIView.as_view(), name='payment_list_create'),

    path('notifications/<int:pk>/mark-as-read/', MarkNotificationReadAPIView.as_view(), name='notification_mark_read'),
]