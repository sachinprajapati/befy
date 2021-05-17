from django.contrib import admin

from .models import *

admin.site.register(Orders)
admin.site.register(OrderItems)
admin.site.register(Address)
