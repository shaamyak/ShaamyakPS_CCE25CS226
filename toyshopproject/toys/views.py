from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Toy, CartItem, Order, UserProfile

def admin_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_staff):
            return redirect('user_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

def home(request):
    toys = Toy.objects.all()[:6]
    return render(request, 'home.html', {'toys': toys})

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('user_dashboard')

    error_message = None

    if request.method == 'POST':
        user_name = request.POST.get('username')
        pass_word = request.POST.get('password')

        user = authenticate(request, username=user_name, password=pass_word)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                if ('admin' in next_url or 'edit' in next_url or 'add' in next_url or 'delete' in next_url) and not (user.is_superuser or user.is_staff):
                    return redirect('user_dashboard')
                return redirect(next_url)
            if user.is_superuser or user.is_staff:
                return redirect('admin_dashboard')
            return redirect('user_dashboard')
        else:
            error_message = "Invalid username or password. Please try again."

    return render(request, 'login.html', {'error': error_message})

def signup_view(request):
    error = None

    if request.method == 'POST':
        data = request.POST.copy()
        if not data.get('password2') and data.get('password1'):
            data['password2'] = data['password1']

        form = UserCreationForm(data)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.get_or_create(user=user)
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                error = errors[0]
                break
    else:
        form = UserCreationForm()

    return render(request, 'signup.html', {'form': form, 'error': error})

def admin_signup_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('user_dashboard')

    error = None

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not confirm_password:
            confirm_password = password

        if not username or not password:
            error = "Please fill in all fields."
        elif password != confirm_password:
            error = "Passwords do not match."
        elif User.objects.filter(username=username).exists():
            error = "A user with that username already exists."
        else:
            user = User.objects.create_superuser(username=username, password=password)
            UserProfile.objects.get_or_create(user=user)
            return redirect('login')

    return render(request, 'admin_signup.html', {'error': error})

def logout_view(request):
    logout(request)
    return redirect('login')

@admin_required
def admin_dashboard(request):
    total_toys = Toy.objects.count()
    total_orders = Order.objects.count()
    total_revenue = sum(float(o.total_price) for o in Order.objects.all())
    total_users = User.objects.filter(is_superuser=False).count()
    recent_orders = Order.objects.select_related('user', 'toy').order_by('-created_at')[:5]
    recent_toys = Toy.objects.all().order_by('-id')[:5]

    context = {
        'total_toys': total_toys,
        'total_orders': total_orders,
        'total_revenue': round(total_revenue, 2),
        'total_users': total_users,
        'recent_orders': recent_orders,
        'recent_toys': recent_toys,
    }
    return render(request, 'admin_dashboard.html', context)

@admin_required
def admin_settings(request):
    message = None
    error = None

    if request.method == 'POST':
        new_username = request.POST.get('username', '').strip()
        new_password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not new_username:
            error = "Username cannot be empty."
        elif User.objects.filter(username=new_username).exclude(id=request.user.id).exists():
            error = "Username is already taken by another user."
        else:
            request.user.username = new_username
            if new_password:
                if not confirm_password:
                    confirm_password = new_password
                if new_password != confirm_password:
                    error = "Passwords do not match."
                else:
                    request.user.set_password(new_password)
                    request.user.save()
                    update_session_auth_hash(request, request.user)
                    message = "Admin username and password updated successfully!"
            else:
                request.user.save()
                message = "Admin username updated successfully!"

    return render(request, 'admin_settings.html', {'message': message, 'error': error})

@admin_required
def admin_orders(request):
    orders = Order.objects.select_related('user', 'toy').order_by('-created_at')
    return render(request, 'admin_orders.html', {'orders': orders})

@admin_required
def admin_update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            order.status = new_status
            order.save()
    return redirect('admin_orders')

@admin_required
def admin_users(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'admin_users.html', {'users_list': users})

@admin_required
def admin_delete_user(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if target_user.id != request.user.id and not target_user.is_superuser:
        target_user.delete()
    return redirect('admin_users')

@admin_required
def toy_list(request):
    toys = Toy.objects.all()
    return render(request, 'toy_list.html', {'toys': toys})

@admin_required
def add_toy(request):
    if request.method == 'POST':
        toy_name = request.POST.get('toy_name')
        age_group = request.POST.get('age_group')
        category = request.POST.get('category')
        price = request.POST.get('price')
        description = request.POST.get('description', '')

        Toy.objects.create(
            toy_name=toy_name,
            age_group=age_group,
            category=category,
            price=price,
            description=description
        )
        return redirect('toy_list')

    return render(request, 'add_toy.html')

@admin_required
def edit_toy(request, id):
    toy = get_object_or_404(Toy, id=id)

    if request.method == 'POST':
        toy.toy_name = request.POST.get('toy_name')
        toy.age_group = request.POST.get('age_group')
        toy.category = request.POST.get('category')
        toy.price = request.POST.get('price')
        toy.description = request.POST.get('description', '')
        toy.save()
        return redirect('toy_list')

    return render(request, 'edit_toy.html', {'toy': toy})

@admin_required
def delete_toy(request, id):
    toy = get_object_or_404(Toy, id=id)
    toy.delete()
    return redirect('toy_list')

@login_required
def user_dashboard(request):
    category = request.GET.get('category')
    search_query = request.GET.get('q')

    toys = Toy.objects.all()
    if category:
        toys = toys.filter(category__iexact=category)
    if search_query:
        toys = toys.filter(toy_name__icontains=search_query)

    categories = Toy.objects.values_list('category', flat=True).distinct()
    cart_count = CartItem.objects.filter(user=request.user).count()
    order_count = Order.objects.filter(user=request.user).count()

    context = {
        'toys': toys,
        'categories': categories,
        'selected_category': category,
        'search_query': search_query,
        'cart_count': cart_count,
        'order_count': order_count,
    }
    return render(request, 'user_dashboard.html', context)

@login_required
def toy_detail(request, id):
    toy = get_object_or_404(Toy, id=id)
    return render(request, 'toy_detail.html', {'toy': toy})

@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('toy')
    total_price = sum(item.subtotal() for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': round(total_price, 2)})

@login_required
def add_to_cart(request, toy_id):
    toy = get_object_or_404(Toy, id=toy_id)
    qty = 1
    if request.method == 'POST':
        try:
            qty = max(1, int(request.POST.get('quantity', 1)))
        except (ValueError, TypeError):
            qty = 1

    cart_item, created = CartItem.objects.get_or_create(user=request.user, toy=toy)
    if not created:
        cart_item.quantity += qty
        cart_item.save()
    else:
        cart_item.quantity = qty
        cart_item.save()

    return redirect('view_cart')

@login_required
def update_cart_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'increase':
            cart_item.quantity += 1
            cart_item.save()
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
    return redirect('view_cart')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    return redirect('view_cart')

@login_required
def place_order(request):
    if request.method == 'POST':
        cart_items = CartItem.objects.filter(user=request.user).select_related('toy')
        if not cart_items.exists():
            return redirect('view_cart')

        for item in cart_items:
            unit_price = item.price_numeric()
            Order.objects.create(
                user=request.user,
                toy=item.toy,
                quantity=item.quantity,
                total_price=unit_price * item.quantity,
                status='Placed'
            )
        cart_items.delete()
        return redirect('user_orders')

    return redirect('view_cart')

@login_required
def buy_now(request, toy_id):
    toy = get_object_or_404(Toy, id=toy_id)
    qty = 1
    if request.method == 'POST':
        try:
            qty = max(1, int(request.POST.get('quantity', 1)))
        except (ValueError, TypeError):
            qty = 1

    try:
        unit_price = float(''.join(c for c in str(toy.price) if c.isdigit() or c == '.'))
    except (ValueError, TypeError):
        unit_price = 0.0

    Order.objects.create(
        user=request.user,
        toy=toy,
        quantity=qty,
        total_price=unit_price * qty,
        status='Placed'
    )
    return redirect('user_orders')

@login_required
def user_orders(request):
    orders = Order.objects.filter(user=request.user).select_related('toy').order_by('-created_at')
    return render(request, 'user_orders.html', {'orders': orders})

@login_required
def user_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    message = None

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.save()

        profile.phone = phone
        profile.address = address
        profile.save()

        message = "Profile updated successfully!"

    return render(request, 'user_profile.html', {'profile': profile, 'message': message})
