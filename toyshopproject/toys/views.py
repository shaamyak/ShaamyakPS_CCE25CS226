from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Toy

def home(request):
    return render(request, 'home.html')

@login_required
def add_toy(request):
    if request.method == 'POST':
        toy_name = request.POST.get('toy_name')
        age_group = request.POST.get('age_group')
        category = request.POST.get('category')
        price = request.POST.get('price')

        Toy.objects.create(
            toy_name=toy_name,
            age_group=age_group,
            category=category,
            price=price
        )
        return redirect('toy_list')

    return render(request, 'add_toy.html')

@login_required
def toy_list(request):
    toys = Toy.objects.all()
    return render(request, 'toy_list.html', {'toys': toys})

@login_required
def edit_toy(request, id):
    toy = get_object_or_404(Toy, id=id)

    if request.method == 'POST':
        toy.toy_name = request.POST.get('toy_name')
        toy.age_group = request.POST.get('age_group')
        toy.category = request.POST.get('category')
        toy.price = request.POST.get('price')
        toy.save()
        return redirect('toy_list')

    return render(request, 'edit_toy.html', {'toy': toy})

@login_required
def delete_toy(request, id):
    toy = get_object_or_404(Toy, id=id)
    toy.delete()
    return redirect('toy_list')

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'signup.html', {'form': form})

def login_view(request):
    error_message = None

    if request.method == 'POST':
        user_name = request.POST.get('username')
        pass_word = request.POST.get('password')

        user = authenticate(request, username=user_name, password=pass_word)

        if user is not None:
            login(request, user)
            return redirect('toy_list')
        else:
            error_message = "Invalid username or password. Please try again."

    return render(request, 'login.html', {'error': error_message})

def logout_view(request):
    logout(request)
    return redirect('login')
