from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('profile/', views.UserProfileListView.as_view(), name='profile-list'),
    path('add-user-profile/', views.add_user_profile, name="add-user-profile"),
    path('user-profile/<int:pk>/', views.UserProfileDetailView.as_view(), name="user-profile"),
    path('profiles/<int:pk>/edit/', views.UserProfileUpdateView.as_view(), name='profile-edit'),
    path('profiles/<int:pk>/delete/', views.UserProfileDeleteView.as_view(), name='profile-delete'),
    path('order-summary/', views.order_summary, name='order-summary'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('succes/', views.PaymentSucces.as_view(), name='payment-success'),
    path('cancel/', views.PaymentCancel.as_view(), name='payment-cancel'),
    path('webhook-stripe/', views.StripeWebhookView.as_view(), name='webhook-stripe'),
    path('order-history/', views.order_history, name='order-history'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)