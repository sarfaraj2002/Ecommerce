from django.contrib import admin
from .models import*
from django.contrib.sessions.models import Session
# Register your models here.

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(Session)
admin.site.register(Images)
admin.site.register(ProductDetails)