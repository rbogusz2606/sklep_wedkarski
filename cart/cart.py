from app.models import Product
from decimal import Decimal
class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get("session_key")

        if not cart:
            cart = self.session["session_key"] = {}

        self.cart = cart

    def add(self, product, quantity):
        product_id = str(product.id)
        
        if quantity <= 0:
            return  # Nie dodawaj produktu, jeśli ilość jest mniejsza lub równa 0

        # Jeśli produkt już istnieje w koszyku, aktualizuj ilość
        if product_id in self.cart:
            self.cart[product_id] = quantity  # Zaktualizuj ilość
        else:
            self.cart[product_id] = quantity
        
        self.save()

    def update(self, product_id, quantity):
        product_id = str(product_id)
        if quantity <= 0:
            self.remove(product_id)
        else:
            if product_id in self.cart:
                self.cart[product_id] = quantity
            self.save()

    def remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        self.session.modified = True

    def __len__(self):
        return sum(self.cart.values())

    @property
    def get_prods(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        return products

    @property
    def get_quants(self):
        return self.cart
    
    def cart_total(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        quantities = self.cart
        total = Decimal(0.0)

        for key, value in quantities.items():
            key = int(key)
            for product in products:
                if product.id == key:
                    total += product.price * value
        return total