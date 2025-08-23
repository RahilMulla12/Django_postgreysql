from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import WindowOrder, Window
from django.db import models



# Home view
def Home(request):
    return render(request, "Home.html")

# Products view
def product(request):
    return render(request, "products.html")

# Contact view (uncomment if needed)
# def contact(request):
#     return render(request, 'contact.html')

# Login view
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('Home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

# Register view
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('login')  # match the name in your urls.py

        my_user = User.objects.create_user(username=username, password=password, email=email)
        my_user.save()
        messages.success(request, "User created successfully!")
        return redirect('login')

    return render(request, 'register.html')

# Logout view
def signout(request):
    logout(request)
    return redirect('Home')
@csrf_exempt




@login_required
def order_windows(request):
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        customer_address = request.POST.get('customer_address')
        customer_phone = request.POST.get('customer_phone')
        email = request.POST.get('customer_email')
        note = request.POST.get('note')

        # Collect all window fields
        windows = []
        index = 1
        base_rate = 0.05  # $0.05 per inch²
        total_price = 0

        while True:
            w_type = request.POST.get(f'window_type_{index}')
            glass_type = request.POST.get(f'glass_type_{index}')
            width = request.POST.get(f'window_width_{index}')
            height = request.POST.get(f'window_height_{index}')

            if not w_type or not glass_type or not width or not height:
                break

            try:
                width = float(width)
                height = float(height)
                price = round(width * height * base_rate, 2)
                total_price += price
                windows.append({
                    'type': w_type,
                    'glass_type': glass_type,
                    'width': width,
                    'height': height,
                    'price': price,
                })
            except ValueError:
                messages.error(request, "Invalid numeric values in window dimensions.")
                return redirect('order_windows')

            index += 1

        if not windows:
            messages.error(request, "You must add at least one window.")
            return redirect('order_windows')

        # Save Order and Windows
        order = WindowOrder.objects.create(
            user=request.user,
            customer_name=customer_name,
            customer_address=customer_address,
            customer_phone=customer_phone,
            customer_email=email,
            note=note,
            total_price=round(total_price, 2)
        )

        for window in windows:
            Window.objects.create(
                order=order,
                type=window['type'],
                glass_type=window['glass_type'],
                width=window['width'],
                height=window['height'],
                price=window['price']
            )

        messages.success(request, f"Order placed successfully! Total: ${round(total_price, 2)}")
        return redirect('payment_page', order_id=order.id)

    return render(request, 'order.html', {'username': request.user.username})



def UserDashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Fetch orders for the logged-in user
    orders = WindowOrder.objects.filter(user=request.user).prefetch_related('windows')
    completed_orders_count = orders.filter(status='Completed').count()
    pending_orders_count = orders.filter(status='Pending').count()
    processing_orders_count = orders.filter(status='Processing').count()
    total_revenue = orders.aggregate(total=models.Sum('total_price'))['total'] or 0

    context = {
        'orders': orders,
        'completed_orders': completed_orders_count,
        'pending_orders': pending_orders_count,
        'processing_orders': processing_orders_count,
        'completed_orders_count': completed_orders_count,
        'order': {'total_price': total_revenue},  # To preserve your {{ order.total_price }} usage
    }

    return render(request, 'UserDashboard.html', context)
from functools import wraps

def superuser_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@superuser_required
def AdminDashboard(request):
    # Fetch all orders for admin view
    orders = WindowOrder.objects.all().prefetch_related('windows')
    Users = User.objects.all()

    #tottal agents
    

    context = { 
        'orders': orders,
        'completed_orders': orders.filter(status='Completed').count(),
        'pending_orders': orders.filter(status='Pending').count(),
        'processing_orders': orders.filter(status='Processing').count(),
        'total_revenue': orders.aggregate(total=models.Sum('total_price'))['total'] or 0,
        'total_agents': User.objects.count(),
        'total_orders': orders.count(),
        'Users': Users,  # Pass all users to the template 
        'username': request.user.username,  # Pass the username for display 
        'email': request.user.email,  # Pass the email for display
        'staff': request.user.is_staff,  # Pass the staff status for display
        'revenue_by_agent': orders.filter(user=request.user).aggregate(total=models.Sum('total_price'))['total'] or 0,
        'agent_sales_count': orders.filter(user=request.user).count(),  # Count of orders by the agent
    }
    return render(request, 'AdminDashboard.html', context)

def confirm_order(request):
     return render(request, 'confirm_order.html', {'username': request.user.username})
    
def payment_page(request, order_id):
    try:
        order = WindowOrder.objects.get(id=order_id, user=request.user)
       
    except WindowOrder.DoesNotExist :
        messages.error(request, "Order not found.")
        return redirect('order_windows')

    return render(request, 'payment.html', {'order': order})

def process_payment(request, order_id):
    if request.method == 'POST':
        # Simulate success or integrate with real payment gateway here
        order = WindowOrder.objects.get(id=order_id, user=request.user)
        order.status = 'Processing'
        order.save()

        messages.success(request, "Payment successful!")
        return redirect('order_success')
