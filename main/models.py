from django.contrib.auth.models import AbstractBaseUser,BaseUserManager, PermissionsMixin
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver

class Category(models.Model):
    name = models.CharField(max_length=100)

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='userprofile')

    full_name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    address = models.TextField()
    

    full_name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return self.full_name

   
    
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=20, choices=[('customer', 'Customer'), ('shop', 'Shop')])
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    is_email_verified = models.BooleanField(default=False)

    address = models.TextField(blank=True, null=True)
    shop_name = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    is_shop_approved = models.BooleanField(default=False)
    gst_number = models.CharField(max_length=20, blank=True, null=True)
    shop_registration_number = models.CharField(max_length=30, blank=True, null=True)
    

    
    

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    def is_otp_valid(self):
        if not self.otp_created_at:
            return False
        return timezone.now() <= self.otp_created_at + timedelta(minutes=10)  # OTP valid for 10 mins


    def __str__(self):
        return self.email

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('plumbing', 'Plumbing'),
        ('electrical', 'Electrical'),
        ('paint', 'Paint & Finishes'),
        ('tools', 'Tools'),
        ('home_appliances', 'Home Appliances'),
        ('building_materials', 'Building Materials')
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='product_images/')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    is_for_shop = models.BooleanField(default=False)
    brand = models.CharField(max_length=100, blank=True)
    retail_price = models.DecimalField(max_digits=10, decimal_places=2, default=000)
    wholesale_price = models.DecimalField(max_digits=10, decimal_places=2,default=000)
    box_quantity = models.PositiveIntegerField(default=1)
    discount = models.DecimalField(max_digits=5, decimal_places=2, help_text="e.g. 10 for 10% off", default = 0.0)
    purchase_link = models.URLField(max_length=500, default='https://maulitraders.org/contact/')


    def __str__(self):
        return self.name



class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

class Expense(models.Model):
    description = models.TextField()
    amount = models.FloatField()
    date = models.DateField()


class SoldProduct(models.Model):
    product_name = models.CharField(max_length=255)
    buyer_name = models.CharField(max_length=255)
    buyer_email = models.EmailField()
    buyer_contact = models.CharField(max_length=20, blank=True, null=True)
    buyer_type = models.CharField(max_length=20, choices=[('retailer', 'Retailer'), ('individual', 'Individual')], default='individual')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    date_sold = models.DateTimeField(auto_now_add=True)
    generated_receipt = models.FileField(upload_to='receipts/', blank=True, null=True)

    def __str__(self):
        return f"{self.product_name} sold to {self.buyer_name}"

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)