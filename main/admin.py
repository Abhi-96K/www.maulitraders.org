from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from .models import SoldProduct

from .models import CustomUser, UserProfile, Product


CustomUser = get_user_model()

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    ordering = ['email']
    actions = ['approve_shops']

    list_display = ('email', 'user_type', 'is_active', 'is_staff', 'is_shop_approved')
    list_filter = ('user_type', 'is_shop_approved', 'is_active', 'is_staff')
    search_fields = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('User Info'), {
            'fields': ('user_type', 'is_shop_approved', 'address', 'shop_name', 'city', 'gst_number', 'shop_registration_number'),
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'user_type'),
        }),
    )

    def approve_shops(self, request, queryset):
        approved_users = []
        for user in queryset:
            if user.user_type == 'shop' and not user.is_shop_approved:
                user.is_shop_approved = True
                user.is_active = True
                user.save()
                approved_users.append(user)

                # ✅ Get full_name from UserProfile (not CustomUser)
                try:
                    user_profile = UserProfile.objects.filter(user=user).first()
                    full_name = user_profile.full_name if user_profile else "Shop Owner"
                except Exception:
                    full_name = "Shop Owner"
                # ✅ Send system-generated email
                send_mail(
                    subject="Your Shop Has Been Approved - Mauli Traders",
                    message=f"""\
Hello {full_name},

Congratulations! 🎉

Your shop registration with Mauli Traders has been successfully approved by our administrator.

You can now log in using your registered email and password to manage your shop, add products, and begin your journey with us.

🔑 Login Access: http://127.0.0.1:8000/login/

We’re excited to have you on board and look forward to a successful collaboration.

If you have any questions or need assistance, feel free to reply to this email or contact our support team.

Warm regards,  
Mauli Traders Team  
""",
                    from_email="1.maulitraders@gmail.com",
                    recipient_list=[user.email],
                    fail_silently=False,
                )

        self.message_user(request, f"{len(approved_users)} shop(s) have been approved and notified.")

    approve_shops.short_description = "Approve selected shops"

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'mobile', 'address')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'retail_price', 'wholesale_price', 'brand')
    list_filter = ('category', 'brand')
    search_fields = ('name', 'brand')

@admin.register(SoldProduct)
class SoldProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'buyer_name', 'price', 'date_sold')
    search_fields = ('buyer_name', 'product_name')