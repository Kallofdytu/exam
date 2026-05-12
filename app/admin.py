from django.contrib import admin
from .models import *

admin.site.register(CustomerProfile)
admin.site.register(Wallet)
admin.site.register(BankCard)
admin.site.register(Transaction)
admin.site.register(PaymentCategory)
admin.site.register(ServiceProvider)
admin.site.register(Payment)
admin.site.register(FavoritePayment)
admin.site.register(Notification)
