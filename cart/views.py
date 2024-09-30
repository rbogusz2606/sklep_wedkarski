from .cart import Cart
from django.shortcuts import render, get_object_or_404
from app.models import Product
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
def cart_summary(request):
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()
        
    context = {
        "cart_products": cart_products,
        "quantities": quantities,
        "totals": totals,
    }
    return render(request, "cart_summary.html", context)
def cart_add(request):
    cart = Cart(request)
    if request.POST.get("action") == "post":
        try:
            product_id = int(request.POST.get("product_id"))
            product_quantity = int(request.POST.get("product_quantity"))

            product = get_object_or_404(Product, id=product_id)

            # Dodaj lub zaktualizuj produkt w koszyku
            cart.add(product=product, quantity=product_quantity)
            updated_cart_quantity = cart.__len__()  # Zaktualizuj liczbę produktów w koszyku

            response = JsonResponse({
                "cart_quantity": updated_cart_quantity,
                "product_quantity": product_quantity,
            })
            return response

        except ValueError:
            return JsonResponse({"error": "Nieprawidłowa ilość. Proszę upewnić się, że wprowadzono liczbę."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)

def cart_update(request):
    cart = Cart(request)
    if request.method == "POST":
        try:
            product_id = request.POST.get("product_id")
            product_qty = request.POST.get("product_qty")

            # Logi do diagnostyki
            print(f"Product ID: {product_id}, Product Quantity: {product_qty}")

            if not product_id or product_qty is None:
                return JsonResponse({"error": "Brak wymaganych danych."}, status=400)

            product_id = int(product_id)
            product_qty = int(product_qty)

            # Upewnij się, że ilość jest większa od 0
            if product_qty <= 0:
                return JsonResponse({"error": "Ilość musi być większa od 0."}, status=400)

            # Dodaj aktualizację ilości do koszyka
            cart.add(product=get_object_or_404(Product, id=product_id), quantity=product_qty)
            return JsonResponse({"message": "Ilość zaktualizowana pomyślnie."})

        except ValueError:
            return JsonResponse({"error": "Nieprawidłowe dane liczbowе."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Nieprawidłowe żądanie."}, status=400)

def cart_remove(request):
    cart = Cart(request)
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        cart.remove(product_id)

        return JsonResponse({'success': True, 'cart_quantity': cart.__len__(), 'total': cart.cart_total()})