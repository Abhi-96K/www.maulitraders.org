from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import CustomUserForm , ShopDetailsForm
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth import logout, authenticate, login
from .models import CustomUser, UserProfile
import random
from .forms import OTPVerificationForm
from django.core.mail import send_mail,  EmailMultiAlternatives
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.template.loader import render_to_string
import os
from django.conf import settings




def home(request):
    return render(request, 'main/home.html')

def about(request):
    return render(request, 'main/about.html')

def products(request):
    return render(request, 'main/products.html')

def contact(request):
    return render(request, 'main/contact.html')

def category_page(request, slug):
    # You can load products related to the category here
    return render(request, 'main/category_page.html', {'slug': slug})

def cart(request):
    return render(request, 'main/cart.html')

def profile(request):
    return render(request, 'main/profile.html')

def register(request):
    return render(request, 'main/register.html')


def register_customer(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            if CustomUser.objects.filter(email=email).exists():
                form.add_error('email', 'This email is already registered.')
            else:
                try:
                    # Step 1: Create inactive user
                    user = CustomUser.objects.create_user(
                        email=email,
                        password=form.cleaned_data['password'],
                        user_type='customer',
                        is_active=False  # Inactive until email verified
                    )

                    # Step 2: Create user profile
                    UserProfile.objects.create(
                        user=user,
                        full_name=form.cleaned_data['full_name'],
                        mobile=form.cleaned_data['mobile'],
                        address=form.cleaned_data['address']
                    )

                    # Step 3: Generate OTP
                    otp = generate_otp()
                    user.otp = otp
                    user.otp_created_at = timezone.now()
                    user.save()

                    # Step 4: Send OTP email
                    send_otp_email(user.email, otp)

                    # Step 5: Store email in session to verify
                    request.session['pending_user_email'] = user.email

                    # Step 6: Redirect to email verification
                    return redirect('verify_email')

                except IntegrityError:
                    form.add_error('email', 'This email is already in use.')
        else:
            messages.error(request, "password mismatched please enter the matching password.")
    else:
        form = CustomUserForm()

    return render(request, 'main/register_customer.html', {'form': form})


def register_s1(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            request.session['shop_register_data'] = {
               
                'email': form.cleaned_data['email'],
                'password': form.cleaned_data['password'],
                'full_name': form.cleaned_data['full_name'],
                'mobile': form.cleaned_data['mobile'],
                'address': form.cleaned_data['address'],
               


            }
            return redirect('register_s2')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserForm()
    return render(request, 'main/register_s1.html', {'form': form})


def register_s2(request):
    if 'shop_register_data' not in request.session:
        return redirect('register_s1')

    if request.method == 'POST':
        form = ShopDetailsForm(request.POST)
        if form.is_valid():
            data = request.session.get('shop_register_data')
            email = data['email']

            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, "This email is already registered.")
                return redirect('register_s1')

            try:
                # Step 1: Create inactive shop user
                user = CustomUser.objects.create_user(
                    email=email,
                    password=data['password'],
                    user_type='shop',
                    is_shop_approved=False,
                    is_active=False  # Wait for email verification
                )

                # Step 2: Save profile
                UserProfile.objects.create(
                    user=user,
                    full_name=data['full_name'],
                    mobile=data['mobile'],
                    address=data['address']
                )

                # Step 3: Save shop details
                user.shop_name = form.cleaned_data['shop_name']
                user.city = form.cleaned_data['city']
                user.gst_number = form.cleaned_data.get('gst_number')
                user.shop_registration_number = form.cleaned_data.get('shop_registration_number')

                # Step 4: Generate OTP
                otp = generate_otp()
                user.otp = otp
                user.otp_created_at = timezone.now()
                user.save()

                # Step 5: Send OTP to email
                send_otp_email(user.email, otp)

                # Step 6: Clear session and redirect
                del request.session['shop_register_data']
                request.session['pending_user_email'] = user.email

                return redirect('verify_email')

            except IntegrityError:
                messages.error(request, "A user with this email already exists.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ShopDetailsForm()

    return render(request, 'main/register_s2.html', {'form': form})
        

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp, full_name=None):
    subject = 'Verify Your Email - Mauli Traders'
    from_email = '1.maulitraders@gmail.com'
    to = [email]

    html_content = render_to_string('main/email_otp_template.html', {
        'full_name':full_name or "Customer",



        'otp': otp,
    })

    msg = EmailMultiAlternatives(subject=subject, body="Your OTP is " + otp, from_email=from_email, to=to)
    msg.attach_alternative(html_content, "text/html")

    

    
    msg.send()

def resend_otp(request):
    email = request.session.get('pending_user_email')
    if not email:
        return redirect('login')

    user = CustomUser.objects.filter(email=email).first()
    if user:
        otp = generate_otp()
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()
        send_otp_email(user.email, otp)
        messages.success(request, "OTP resent successfully.")
    return redirect('verify_email')



from django.utils.timezone import now
from datetime import timedelta

def verify_email(request):
    email = request.session.get('pending_user_email')

    if not email:
        messages.error(request, "No pending email verification.")
        return redirect('login')

    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        try:
            user = CustomUser.objects.get(email=email)
            if user.otp == otp_entered and not user.is_email_verified:
                # Check OTP expiration
                if timezone.now() - user.otp_created_at > timedelta(minutes=10):
                    messages.error(request, "OTP has expired. Please resend.")
                    return redirect('resend_otp')

                # Email verified
                user.is_email_verified = True
                user.otp = None
                user.otp_created_at = None

                if user.user_type == 'customer':
                    user.is_active = True  # ✅ Customers become active after verification
                    user.save()
                    del request.session['pending_user_email']
                    messages.success(request, "Email verified successfully! You can now login.")
                    return redirect('login')

                elif user.user_type == 'shop':
                    user.is_active = False  # ❌ Shops remain inactive until admin approves
                    user.save()
                    del request.session['pending_user_email']
                    messages.success(
                        request,
                        "Your registration has been verified. Now it's pending admin approval. You'll be notified once approved."
                    )
                    return redirect('login')

            else:
                messages.error(request, "Invalid OTP. Please try again.")

        except CustomUser.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('login')

    return render(request, 'main/verify_email.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']   # Assuming you're using email as username
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        


        if user is not None:
            if user.user_type == 'shop' and not user.is_shop_approved:
                messages.error(request, 'Your shop is not verified yet. Please wait for admin approval.')
                return redirect('login')
            login(request, user)
            return redirect('login')
        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('login')
        
    if not user.is_verified:
        raise ValidationError("Your email is not verified yet.")

    
    return render(request, 'main/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')


def terms_conditions(request):
    return render(request, 'main/terms.html')

@login_required
def customer_profile(request):
    if request.user.user_type != 'customer':
        return redirect('home') # Or show error
    return render(request, 'main/customer_profile.html', {'user': request.user})

@login_required
def shop_profile(request):
    if request.user.user_type != 'shop':
        return redirect('home') # Or show error
    return render(request, 'main/shop_profile.html', {'user': request.user})
