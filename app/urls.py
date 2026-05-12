from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomerProfileViewSet, WalletViewSet, BankCardViewSet,
    ServiceProviderViewSet, FavoritePaymentViewSet, NotificationViewSet,
    payment_category_list, payment_category_detail,
    TopUpAPIView, TransferAPIView, TransactionListAPIView,
    PaymentListCreateAPIView, MarkNotificationReadAPIView
)

router = DefaultRouter()
router.register(r'profiles', CustomerProfileViewSet)
router.register(r'wallets', WalletViewSet)
router.register(r'cards', BankCardViewSet)
router.register(r'providers', ServiceProviderViewSet)
router.register(r'favorites', FavoritePaymentViewSet)
router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    path('', include(router.urls)),

    path('payment-categories/', payment_category_list),
    path('payment-categories/<int:pk>/', payment_category_detail),

    path('transactions/', TransactionListAPIView.as_view()),
    path('transactions/top-up/', TopUpAPIView.as_view()),
    path('transactions/transfer/', TransferAPIView.as_view()),

    path('payments/', PaymentListCreateAPIView.as_view()),
    path('notifications/<int:pk>/mark-as-read/', MarkNotificationReadAPIView.as_view()),
]