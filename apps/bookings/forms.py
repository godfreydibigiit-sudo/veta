"""
Forms for booking management.
"""
from django import forms
from django.utils import timezone
from apps.bookings.models import Booking


class BookingCreateForm(forms.ModelForm):
    """Form for guests to create a booking."""
    
    check_in = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': timezone.now().date().isoformat()
        })
    )
    
    check_out = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': timezone.now().date().isoformat()
        })
    )
    
    guest_count = forms.IntegerField(
        required=True,
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Number of guests'
        })
    )
    
    special_requests = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any special requests? (optional)'
        })
    )
    
    class Meta:
        model = Booking
        fields = ['check_in', 'check_out', 'guest_count', 'special_requests']
    
    def clean(self):
        """Validate booking dates."""
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        
        if check_in and check_out:
            if check_in >= check_out:
                raise forms.ValidationError(
                    'Check-out date must be after check-in date.'
                )
            
            if check_in < timezone.now().date():
                raise forms.ValidationError(
                    'Check-in date cannot be in the past.'
                )
            
            # Maximum advance booking (1 year)
            max_date = timezone.now().date() + timezone.timedelta(days=365)
            if check_in > max_date:
                raise forms.ValidationError(
                    'Bookings can only be made up to 1 year in advance.'
                )
        
        return cleaned_data


class BookingStatusForm(forms.Form):
    """Form for staff to update booking status."""
    
    ACTION_CHOICES = [
        ('approve', 'Approve Booking'),
        ('cancel', 'Cancel Booking'),
        ('check_in', 'Check In Guest'),
        ('check_out', 'Check Out Guest'),
        ('mark_paid', 'Mark as Paid'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Reason (required for cancellation)'
        })
    )
    
    def clean(self):
        """Validate action-specific requirements."""
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        reason = cleaned_data.get('reason')
        
        if action == 'cancel' and not reason:
            raise forms.ValidationError(
                'Please provide a reason for cancellation.'
            )
        
        return cleaned_data


class BookingSearchForm(forms.Form):
    """Form for searching bookings."""
    
    query = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by reference ID, guest name, or phone'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + list(Booking.STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )