from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Toy

# 1. Home page view (anyone can visit this page)
def home(request):
    # Render the home.html template
    return render(request, 'home.html')


# 2. Add Toy view (only logged-in users can add toys)
@login_required
def add_toy(request):
    # When user submits the form (POST method)
    if request.method == 'POST':
        # Get data entered by the user in the form fields
        toy_name = request.POST.get('toy_name')
        age_group = request.POST.get('age_group')
        category = request.POST.get('category')
        price = request.POST.get('price')

        # Save the new toy into the database
        Toy.objects.create(
            toy_name=toy_name,
            age_group=age_group,
            category=category,
            price=price
        )

        # After saving, go to the toy list page
        return redirect('toy_list')

    # If it is a normal page visit (GET method), show the empty form
    return render(request, 'add_toy.html')


# 3. View All Toys (only logged-in users can view)
@login_required
def toy_list(request):
    # Fetch all toy records from the database
    toys = Toy.objects.all()

    # Pass toys list to the toy_list.html template
    return render(request, 'toy_list.html', {'toys': toys})


# 4. Edit Toy view (only logged-in users can edit)
@login_required
def edit_toy(request, id):
    # Fetch the specific toy by its ID or return 404 if not found
    toy = get_object_or_404(Toy, id=id)

    # When user submits the updated form
    if request.method == 'POST':
        # Update the toy fields with new data
        toy.toy_name = request.POST.get('toy_name')
        toy.age_group = request.POST.get('age_group')
        toy.category = request.POST.get('category')
        toy.price = request.POST.get('price')

        # Save the changes to the database
        toy.save()

        # Redirect back to the toy list page
        return redirect('toy_list')

    # Show the form pre-filled with the current toy details
    return render(request, 'edit_toy.html', {'toy': toy})


# 5. Delete Toy view (only logged-in users can delete)
@login_required
def delete_toy(request, id):
    # Fetch the specific toy by ID
    toy = get_object_or_404(Toy, id=id)

    # Remove the toy from the database
    toy.delete()

    # Redirect back to the toy list page
    return redirect('toy_list')


# 6. Signup view (new user registration using UserCreationForm)
def signup_view(request):
    # When user submits the signup form
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        # Check if form data is valid (passwords match, username unique)
        if form.is_valid():
            # Save the new user
            form.save()
            # Redirect user to login page after successful registration
            return redirect('login')
    else:
        # Show an empty signup form
        form = UserCreationForm()

    return render(request, 'signup.html', {'form': form})


# 7. Login view (authenticate existing user)
def login_view(request):
    error_message = None

    # When user submits login form
    if request.method == 'POST':
        # Get username and password from form
        user_name = request.POST.get('username')
        pass_word = request.POST.get('password')

        # Check if username and password are correct
        user = authenticate(request, username=user_name, password=pass_word)

        if user is not None:
            # Log the user into the session
            login(request, user)
            # Redirect to the toy list page
            return redirect('toy_list')
        else:
            # Set error message if credentials do not match
            error_message = "Invalid username or password. Please try again."

    # Show login page with error message if any
    return render(request, 'login.html', {'error': error_message})


# 8. Logout view
def logout_view(request):
    # End user session
    logout(request)
    # Redirect back to login page
    return redirect('login')
