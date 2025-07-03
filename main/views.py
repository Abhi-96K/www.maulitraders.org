from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserForm , ShopDetailsForm
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth import logout, authenticate, login
from .models import CustomUser, UserProfile, Product, SoldProduct
import random
from django.core.mail import  EmailMultiAlternatives, EmailMessage
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from datetime import timedelta
from django.template.loader import render_to_string
from django.conf import settings
from django.shortcuts import render
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from .utils.receipt_generator import generate_receipt_pdf
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.utils.safestring import mark_safe
import json






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


#products

def appliances(request):
    user = request.user
    if user.is_authenticated and hasattr(user, 'user_type'):
        if user.user_type == 'shop':
            products = Product.objects.filter(is_for_shop=True, category='home_appliances')
        else:
            products = Product.objects.filter(is_for_shop=False, category='home_appliances')
    else:
        products = Product.objects.filter(is_for_shop=False, category='home_appliances')  # Guest = customer view

    return render(request, 'main/appliances.html', {
        'products': products,
        'user_type': user.user_type if user.is_authenticated else 'guest'
    })


def electrical(request):
    user = request.user
    if user.is_authenticated and hasattr(user, 'user_type'):
        if user.user_type == 'shop':
            products = Product.objects.filter(is_for_shop=True)
        else:
            products = Product.objects.filter(is_for_shop=False)
    else:
        products = Product.objects.filter(is_for_shop=False)  # Guest = customer view

    return render(request, 'main/electrical.html', {'products': products, 'user_type': user.user_type if user.is_authenticated else 'guest'})


def building(request):
    user = request.user
    if user.is_authenticated and hasattr(user, 'user_type'):
        if user.user_type == 'shop':
            products = Product.objects.filter(is_for_shop=True)
        else:
            products = Product.objects.filter(is_for_shop=False)
    else:
        products = Product.objects.filter(is_for_shop=False)  # Guest = customer view

    return render(request, 'main/building.html', {'products': products, 'user_type': user.user_type if user.is_authenticated else 'guest'})

def paint(request):
    user = request.user
    if user.is_authenticated and hasattr(user, 'user_type'):
        if user.user_type == 'shop':
            products = Product.objects.filter(is_for_shop=True)
        else:
            products = Product.objects.filter(is_for_shop=False)
    else:
        products = Product.objects.filter(is_for_shop=False)  # Guest = customer view

    return render(request, 'main/paint.html', {'products': products, 'user_type': user.user_type if user.is_authenticated else 'guest'})

def tool(request):
    user = request.user
    if user.is_authenticated and hasattr(user, 'user_type'):
        if user.user_type == 'shop':
            products = Product.objects.filter(is_for_shop=True)
        else:
            products = Product.objects.filter(is_for_shop=False)
    else:
        products = Product.objects.filter(is_for_shop=False)  # Guest = customer view

    return render(request, 'main/tool.html', {'products': products, 'user_type': user.user_type if user.is_authenticated else 'guest'})

def pumps(request):
    user = request.user
    if user.is_authenticated and hasattr(user, 'user_type'):
        if user.user_type == 'shop':
            products = Product.objects.filter(is_for_shop=True)
        else:
            products = Product.objects.filter(is_for_shop=False)
    else:
        products = Product.objects.filter(is_for_shop=False)  # Guest = customer view

    return render(request, 'main/pumps.html', {'products': products, 'user_type': user.user_type if user.is_authenticated else 'guest'})


def plumbing(request):
    user = request.user
    if user.is_authenticated and hasattr(user, 'user_type'):
        if user.user_type == 'shop':
            products = Product.objects.filter(is_for_shop=True)
        else:
            products = Product.objects.filter(is_for_shop=False)
    else:
        products = Product.objects.filter(is_for_shop=False)  # Guest = customer view

    return render(request, 'main/plumbing.html', {'products': products, 'user_type': user.user_type if user.is_authenticated else 'guest'})

def machineries(request):
    user = request.user
    if user.is_authenticated and hasattr(user, 'user_type'):
        if user.user_type == 'shop':
            products = Product.objects.filter(is_for_shop=True)
        else:
            products = Product.objects.filter(is_for_shop=False)
    else:
        products = Product.objects.filter(is_for_shop=False)  # Guest = customer view

    return render(request, 'main/machineries.html', {'products': products, 'user_type': user.user_type if user.is_authenticated else 'guest'})

def farming(request):
    user = request.user
    if user.is_authenticated and hasattr(user, 'user_type'):
        if user.user_type == 'shop':
            products = Product.objects.filter(is_for_shop=True)
        else:
            products = Product.objects.filter(is_for_shop=False)
    else:
        products = Product.objects.filter(is_for_shop=False)  # Guest = customer view

    return render(request, 'main/farming.html', {'products': products, 'user_type': user.user_type if user.is_authenticated else 'guest'})

def online_purchase(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        buyer_name = request.POST.get('buyer_name')
        buyer_email = request.POST.get('buyer_email')
        

        # Create sale record
        sale = SoldProduct.objects.create(
            product_name=product.name,
            buyer_name=buyer_name,
            buyer_email=buyer_email,
            price=product.retail_price,
            quantity=1
        )

        # Generate receipt
        pdf_buffer = generate_receipt_pdf(sale)
        sale.generated_receipt.save(f"receipt_{sale.id}.pdf", ContentFile(pdf_buffer.read()))
        sale.save()

        # Send Email
        email = EmailMessage(
            f"Your Purchase Receipt from Mauli Traders",
            "Thank you for your purchase. Please find your receipt attached.",
            'yourshop@example.com',
            [buyer_email],
        )
        email.attach(f"receipt_{sale.id}.pdf", pdf_buffer.getvalue(), 'application/pdf')
        email.send()

        # Remove product
        product.delete()

        messages.success(request, "Purchase successful! Receipt sent to your email.")
        return redirect('home')
    else:
        product = get_object_or_404(Product, id=product_id)
        return render(request, 'main/online_purchase.html', {'product': product})
    

@staff_member_required
def manual_billing(request):
    from django.db.models import Q
    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(brand__icontains=query)
        )
    else:
        products = Product.objects.all()

    if request.method == 'POST':
        buyer_name = request.POST.get('buyer_name')
        buyer_email = request.POST.get('buyer_email')
        buyer_contact = request.POST.get('buyer_contact')
        buyer_type = request.POST.get('buyer_type')
        product_data_json = request.POST.get('product_data')

        if not product_data_json or product_data_json.strip() == "[]":
            messages.error(request, "No products added to bill.")
            return redirect('manual_billing')

        try:
            product_data = json.loads(product_data_json)
        except json.JSONDecodeError:
            messages.error(request, "Invalid product data.")
            return redirect('manual_billing')

        if not product_data:
            messages.error(request, "No products in bill.")
            return redirect('manual_billing')

        sold_items = []
        errors = []

        with transaction.atomic():
            for item in product_data:
                try:
                    product_id = item.get('id')
                    quantity = int(item.get('quantity'))
                    product = Product.objects.select_for_update().get(id=product_id)
                except (ValueError, Product.DoesNotExist):
                    errors.append(f"Invalid product ID: {product_id}")
                    continue

                if quantity > product.box_quantity:
                    errors.append(f"Not enough stock for {product.name}. Available: {product.box_quantity}")
                    continue

                total_price = product.retail_price * quantity

                sale = SoldProduct.objects.create(
                    product_name=product.name,
                    buyer_name=buyer_name,
                    buyer_email=buyer_email,
                    buyer_contact=buyer_contact,
                    price=total_price,
                    quantity=quantity,
                    buyer_type=buyer_type,

                    
                )
                sold_items.append(sale)

                # Update stock
                product.box_quantity -= quantity
                if product.box_quantity <= 0:
                    product.delete()
                else:
                    product.save()

            if errors:
                for e in errors:
                    messages.error(request, e)
                if not sold_items:
                    return redirect('manual_billing')

            # Create a single PDF receipt for all items
            pdf_buffer = generate_receipt_pdf(sold_items, buyer_name=buyer_name, buyer_contact=buyer_contact, buyer_email=buyer_email)
            buyer_type=buyer_type
            for sale in sold_items:
                sale.generated_receipt.save(f"receipt_{sale.id}.pdf", ContentFile(pdf_buffer.read()))
                sale.save()

            receipt_url = sold_items[0].generated_receipt.url
            messages.success(request, mark_safe(f'Bill generated for {buyer_name}. <a href="{receipt_url}" target="_blank">Download Receipt</a>'))

        return redirect('manual_billing')

    # GET request
    return render(request, 'main/manual_billing.html', {'products': products})