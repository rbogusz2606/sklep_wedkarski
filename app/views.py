from django.shortcuts import render, redirect
from . models import  Product,  Category
from django.views.generic import DetailView
from .forms import UserRegistration
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

@login_required
def view(request):
    return render(request, "docs/home.html")

@login_required
def Rods_view(request):
    product_instance = Category.objects.get(id=1)
    rods_filter = Product.objects.filter(category=product_instance)
    return render(request, 'docs/all_rods.html', {'rods_filter': rods_filter})

@login_required
def Rells_view(request):
    product_instance = Category.objects.get(id=2)
    rells_filter = Product.objects.filter(category=product_instance)
    return render(request, 'docs/all_rells.html', {'rells_filter': rells_filter})

class ProductDetailView(LoginRequiredMixin,DetailView):
    model = Product
    template_name = 'docs/product_detail.html'
    context_object_name = 'product'

def register(request):
    if request.method == 'POST':
        form = UserRegistration(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                return redirect('login')
            except IntegrityError:
                form.add_error(None, 'Username already exists.')
    else:
        form = UserRegistration()
    
    return render(request, 'docs/sign_up.html', {'form': form})

@csrf_exempt
def loginView(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Invalid username or password")
    else:
        form = AuthenticationForm()

    return render(request, 'docs/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
