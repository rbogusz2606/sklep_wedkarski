from .cart import Cart

#tworzenie context processors aby liczba produktów w koszyku działała na każdej stronie

def cart(request):
    return{'cart': Cart(request)}