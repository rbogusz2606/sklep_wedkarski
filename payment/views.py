from django.shortcuts import render, redirect
from .forms import UserProfileForm
from django.contrib import messages
from django.views.generic.edit import UpdateView, DeleteView, UpdateView
from django.views.generic.detail import DetailView
from .models import UserProfile, OrderItem
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from cart.cart import Cart
from .models import UserProfile, Order
from django.views.generic import TemplateView
from django.urls import reverse
import uuid
from django.http import JsonResponse
import logging
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

@login_required
def add_user_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user  
            user_profile.save()
            messages.success(request, "Udało Ci się utworzyć profil użytkownika")  
            return redirect("profile-list")
    else:
        form = UserProfileForm()
    
    return render(request, 'add_user_profile.html', {'form': form})


class UserProfileListView(LoginRequiredMixin,ListView):
    model = UserProfile
    template_name = 'user_profile_list.html'
    context_object_name = 'profiles'

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

class UserProfileDetailView(LoginRequiredMixin,DetailView):
    model = UserProfile
    template_name = 'user_profile_detail.html'
    context_object_name = 'profile'

class UserProfileUpdateView(LoginRequiredMixin,UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'user_profile_update.html'
    success_url = reverse_lazy('profile-list')

class UserProfileDeleteView(LoginRequiredMixin,DeleteView):
    model = UserProfile
    template_name = 'user_profile_delete.html'
    success_url = reverse_lazy('profile-list')

import stripe
from django.conf import settings
from django.shortcuts import render, redirect

@login_required
def order_summary(request):
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()
    try:
        userprofile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        userprofile = None

    context = {
        "cart_products": cart_products,
        "quantities": quantities,
        "totals": totals,
        "userprofile" : userprofile,
    }

    return render(request, "order_summary.html", context)

@login_required
def create_checkout_session(request):
    order_number = str(uuid.uuid4())[:8]
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants

    total_amount = cart.cart_total()

    # Tworzenie zamówienia
    order = Order.objects.create(
        user=request.user,
        order_number=order_number,
        total_amount=total_amount,
        payment_status='pending'
    )

    # Tworzenie pozycji zamówienia
    for product in cart_products:
        quantity = quantities[str(product.id)]
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price
        )

    # Tworzenie line_item dla Stripe (jeden z łączną kwotą)
    product_names = ', '.join([f"{product.name} (x{quantities[str(product.id)]})" for product in cart_products])

    total_amount_grosze = int(total_amount * 100)

    line_items = [{
        'price_data': {
            'currency': 'pln',
            'product_data': {
                'name': product_names,
            },
            'unit_amount': total_amount_grosze,
        },
        'quantity': 1,
    }]

    # Tworzenie sesji Stripe Checkout
    stripe.api_key = settings.STRIPE_SECRET_KEY

    session = stripe.checkout.Session.create(
        payment_method_types=['card', 'blik'],
        line_items=line_items,
        mode='payment',
        success_url=request.build_absolute_uri(reverse('payment-success')),
        cancel_url=request.build_absolute_uri(reverse('payment-cancel')),
        metadata={
            'order_number': order_number,
            'user_id': request.user.id,
        }
    )

    return redirect(session.url, code=303)


class PaymentSucces(LoginRequiredMixin,TemplateView):
    template_name = "payment_succes.html"

class PaymentCancel(LoginRequiredMixin,TemplateView):
    template_name = "payment_cancel.html"

logger = logging.getLogger(__name__)


stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
class StripeWebhookView(View):
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            # Niepoprawny ładunek
            return JsonResponse({'status': 'invalid payload'}, status=400)
        except stripe.error.SignatureVerificationError:
            # Niepoprawna sygnatura
            return JsonResponse({'status': 'invalid signature'}, status=400)

        # Obsługa zdarzeń
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            handle_successful_payment(payment_intent)  # Obsługa sukcesu płatności

        return JsonResponse({'status': 'success'})

def handle_successful_payment(payment_intent):
    try:
        order = Order.objects.get(stripe_payment_intent=payment_intent['id'])
        order.status = 'zapłacone'
        order.save()
    except:
        pass

@login_required
def order_history(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')  # Zamówienia posortowane od najnowszych

    # Przekazujemy zamówienia do szablonu
    return render(request, 'order_history.html', {'orders': orders})