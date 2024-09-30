from django.contrib import admin
from .models import UserProfile, Order

admin.site.register(UserProfile)
admin.site.register(Order)