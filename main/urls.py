from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    #nav views
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('products/', views.products, name='products'),
    path('cart/', views.cart, name='cart'),
    path('profile/', views.profile, name='profile'),
    path('contact', views.contact, name= 'contact'),

    # products
    path('appliances/', views.appliances, name='appliances'),
    path('electrical/', views.electrical, name='electrical'),
    path('building/', views.building, name='building'),
    path('paint/', views.paint, name='paint'),
    path('tool/', views.tool, name='tool'),
    path('pumps/', views.pumps, name='pumps'),
    path('plumbing/',views.plumbing, name='plumbing'),
    path('machineries/',views.machineries, name='machineries'),
    path('farming/',views.farming, name='farming'),

    # Register view
    path('register/', views.register, name='register'),
    path('register/customer/', views.register_customer, name='register_customer'),

    path('verify-email/', views.verify_email, name='verify_email'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),

   
    path('register/shop1/', views.register_s1, name='register_s1'),
    path('register/shop2/', views.register_s2, name='register_s2'),

    #Profile view
    path('profile/customer/', views.customer_profile, name='customer_profile'),
    path('profile/shop/', views.shop_profile, name='shop_profile'),


    path('terms/', views.terms_conditions, name='terms_conditions'),

    # Login view (using Django's built-in login view)
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),

    # Logout view
    path('logout/', views.logout_view, name='logout'),

    path('purchase/<int:product_id>/', views.online_purchase, name='online_purchase'),
    path('billing/', views.manual_billing, name='manual_billing'),

]

