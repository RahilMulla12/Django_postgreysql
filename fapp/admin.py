from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import WindowOrder, Window

class WindowInline(admin.TabularInline):
    model = Window
    extra = 1  # Number of extra blank window forms in admin
    readonly_fields = ('price',)  # Make price readonly if you calculate it in views

@admin.register(WindowOrder)
class WindowOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'customer_phone', 'created_at', 'total_price')
    search_fields = ('customer_name', 'customer_phone')
    list_filter = ('created_at',)
    inlines = [WindowInline]

@admin.register(Window)
class WindowAdmin(admin.ModelAdmin):
    list_display = ('order', 'type', 'width', 'height', 'price')
    search_fields = ('type', 'order__customer_name')
