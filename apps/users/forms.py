"""
Forms for user authentication and registration.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from apps.users.models import User
from apps.core.validators import validate_phone_number


class GuestRegistrationForm(UserCreationForm):
    """Registration form for guest users."""
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter first name'
        })
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter last name'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email address'
        })
    )
    
    phone = forms.CharField(
        max_length=15,
        required=True,
        validators=[validate_phone_number],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., +255712345678 or 0712345678'
        })
    )
    
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Your address (optional)'
        })
    )
    
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )
    
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 
            'phone', 'address', 'password1', 'password2'
        ]
    
    def clean_email(self):
        """Validate email is unique."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email
    
    def clean_phone(self):
        """Validate phone number is unique."""
        phone = self.cleaned_data.get('phone')
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError('This phone number is already registered.')
        return phone
    
    def save(self, commit=True):
        """Save user with guest role."""
        user = super().save(commit=False)
        user.role = 'guest'
        user.username = self.cleaned_data['email']  # Use email as username
        if commit:
            user.save()
        return user


class StaffRegistrationForm(UserCreationForm):
    """Form for admin to register staff members."""
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter first name'
        })
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter last name'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter staff email'
        })
    )
    
    phone = forms.CharField(
        max_length=15,
        required=True,
        validators=[validate_phone_number],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., +255712345678'
        })
    )
    
    position = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Staff position/title'
        })
    )
    
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )
    
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email',
            'phone', 'position', 'password1', 'password2'
        ]
    
    def save(self, commit=True):
        """Save user with staff role."""
        user = super().save(commit=False)
        user.role = 'staff'
        user.username = self.cleaned_data['email']
        user.is_staff = True
        user.position = self.cleaned_data.get('position', '')
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    """Custom login form with email/phone authentication."""
    
    username = forms.CharField(
        label='Email or Phone',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email or phone number'
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )
    
    def clean(self):
        """Authenticate user with email or phone."""
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            # Try to find user by email or phone
            user = User.objects.filter(email=username).first() or \
                   User.objects.filter(phone=username).first()
            
            if user:
                self.user_cache = authenticate(
                    self.request, 
                    username=user.email, 
                    password=password
                )
                
                if self.user_cache is None:
                    raise forms.ValidationError(
                        'Invalid password. Please try again.',
                        code='invalid_login'
                    )
                elif not self.user_cache.is_active:
                    raise forms.ValidationError(
                        'This account is inactive.',
                        code='inactive'
                    )
                
                # Check if staff is active
                if self.user_cache.is_staff_user() and not getattr(
                    self.user_cache, 'is_staff_active', True
                ):
                    raise forms.ValidationError(
                        'Your staff account has been deactivated.',
                        code='staff_inactive'
                    )
            else:
                raise forms.ValidationError(
                    'No account found with this email or phone.',
                    code='invalid_login'
                )
        
        return self.cleaned_data


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile."""
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    phone = forms.CharField(
        max_length=15,
        required=True,
        validators=[validate_phone_number],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2
        })
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'address']
    
    def clean_phone(self):
        """Validate phone number uniqueness excluding current user."""
        phone = self.cleaned_data.get('phone')
        if User.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This phone number is already in use.')
        return phone