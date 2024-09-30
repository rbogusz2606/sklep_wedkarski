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
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import logging

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


class UserProfileListView(ListView):
    model = UserProfile
    template_name = 'user_profile_list.html'
    context_object_name = 'profiles'

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

class UserProfileDetailView(DetailView):
    model = UserProfile
    template_name = 'user_profile_detail.html'
    context_object_name = 'profile'

class UserProfileUpdateView(UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'user_profile_update.html'
    success_url = reverse_lazy('profile-list')

class UserProfileDeleteView(DeleteView):
    model = UserProfile
    template_name = 'user_profile_delete.html'
    success_url = reverse_lazy('profile-list')

import stripe
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse

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


class PaymentSucces(TemplateView):
    template_name = "payment_succes.html"

class PaymentCancel(TemplateView):
    template_name = "payment_cancel.html"

logger = logging.getLogger(__name__)

@csrf_exempt
def stripe_webhook(request):
    # Pobieranie payloadu i nagłówka podpisu
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    if not sig_header:
        logger.error("Brak nagłówka podpisu Stripe")
        return HttpResponse(status=400)

    # Weryfikacja podpisu i konstrukcja eventu
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Nieprawidłowy payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Nieprawidłowy podpis Stripe: {e}")
        return HttpResponse(status=400)

    # Obsługa eventu 'checkout.session.completed'
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Pobieranie danych z metadata
        metadata = session.get('metadata', {})
        order_number = metadata.get('order_number')
        user_id = metadata.get('user_id')

        if not order_number or not user_id:
            logger.error("Brak 'order_number' lub 'user_id' w metadata")
            return HttpResponse(status=400)

        try:
            # Pobieranie zamówienia na podstawie order_number i user_id
            order = Order.objects.get(order_number=order_number, user_id=user_id)
            # Aktualizacja statusu płatności
            order.payment_status = 'paid'
            order.save()
            logger.info(f"Zamówienie {order_number} zostało zaktualizowane jako opłacone")
        except Order.DoesNotExist:
            logger.error(f"Zamówienie o numerze {order_number} nie istnieje")
            return HttpResponse(status=400)
        except Exception as e:
            logger.error(f"Błąd podczas aktualizacji zamówienia: {e}")
            return HttpResponse(status=500)
    else:
        logger.warning(f"Nieobsługiwany typ eventu: {event['type']}")

    # Zwracanie odpowiedzi 200 OK
    return HttpResponse(status=200)

def order_history(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')  # Zamówienia posortowane od najnowszych

    # Przekazujemy zamówienia do szablonu
    return render(request, 'order_history.html', {'orders': orders})