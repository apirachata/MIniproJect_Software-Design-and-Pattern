from django.urls import path
from menuapp import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('customer/', views.customer_menu, name='customer_menu'),
    path('order/', views.place_order, name='place_order'),
    path('staff_login/', views.staff_login, name='staff_login'),
    path('staff/', views.staff_dashboard, name='staff_dashboard'),
    path('staff_logout/', views.staff_logout, name='staff_logout'),
]
