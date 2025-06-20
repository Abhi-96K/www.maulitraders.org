from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


from .models import UserProfile
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

# class CustomUserForm(forms.ModelForm)

# class CustomUserForm(forms.ModelForm):
#     full_name = forms.CharField(max_length=100, required=True, label='Full Name')
#     address = forms.CharField(widget=forms.Textarea, required=True, label='Address')
#     mobile = forms.CharField(max_length=15, required=True, label='Mobile Number')
#     email = forms.EmailField(required=True, label='Email')
    
   
#     password = forms.CharField(widget=forms.PasswordInput, label='Password')
#     confirm_password = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

#     class Meta:
#         model = User
#         fields = ['full_name', 'address', 'email', 'mobile', 'password', 'confirm_password']

#     def clean_password(self):
#         password = self.cleaned_data.get("password")
#         if password and len(password) < 8:
#             raise forms.ValidationError("Password must be at least 8 characters long.")
#         return password

#     def clean(self):
#         cleaned_data = super().clean()
#         password = cleaned_data.get("password")
#         confirm_password = cleaned_data.get("confirm_password")
#         if password and confirm_password and password != confirm_password:
#             raise forms.ValidationError("Passwords do not match.")
#         return password

class CustomUserForm(forms.Form):
    full_name = forms.CharField(max_length=100, required=True, label='Full Name')
    address = forms.CharField(widget=forms.Textarea, required=True, label='Address')
    mobile = forms.CharField(max_length=15, required=True, label='Mobile Number')
    email = forms.EmailField(required=True, label='Email')
    
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password and len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data



class ShopDetailsForm(forms.Form):
    shop_name = forms.CharField(max_length=100, required=True, label='Shop Name')
    city = forms.CharField(max_length=100, required=True, label='City')
    gst_number = forms.CharField(max_length=20, required=False, label='GST Number (Optional)')
    shop_registration_number = forms.CharField(max_length=30, required=False, label='Shop Registration No. (Optional)')

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password and len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'shop'
        user.is_active = False  # Disabled login until verified
        user.is_shop_approved = False
        if commit:
            user.save()
        return user
    
class OTPVerificationForm(forms.Form):
    otp = forms.CharField(max_length=6, label="Enter OTP sent to your email")

