from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.view, name="home"),
    path('wedki', views.Rods_view, name="wedki"),
    path('kolowrotki', views.Rells_view, name="kolowrotki"),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('sign_up/', views.register, name='sign_up'),
    path('login/', views.loginView, name='login'),
    path('logout/', views.logout_view, name='logout'),

 ]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)