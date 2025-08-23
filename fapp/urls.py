from django.urls import path   # ✅ correct import
from fapp import views  # only import views
from django.contrib import admin  # admin import must come from django.contrib

urlpatterns = [
    path("", views.Home, name="Home"),
    path("product/", views.product, name="product"),
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path("signout/", views.signout, name="signout"),
    path("order_windows/", views.order_windows, name="order_windows"),
    path("UserDashboard/", views.UserDashboard, name="UserDashboard"),
    path("AdminDashboard/", views.AdminDashboard, name="AdminDashboard"),
    path("confirm_order/", views.confirm_order, name="confirm_order"),
    path("pay/<int:order_id>/", views.payment_page, name="payment_page"),
    path("process-payment/<int:order_id>/", views.process_payment, name="process_payment"),
]