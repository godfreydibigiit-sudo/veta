"""
Forms for room management.
"""
from django import forms
from apps.rooms.models import Room
from apps.core.constants import ROOM_TYPES, ROOM_STATUS


class RoomForm(forms.ModelForm):
    """Form for adding and editing rooms."""
    
    room_number = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter room number (e.g., 101)'
        })
    )
    
    room_type = forms.ChoiceField(
        choices=ROOM_TYPES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    floor = forms.IntegerField(
        required=True,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Floor number'
        })
    )
    
    price_per_night = forms.DecimalField(
        required=True,
        min_value=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Price in TZS'
        })
    )
    
    capacity = forms.IntegerField(
        required=True,
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Maximum guests'
        })
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Room description and features'
        })
    )
    
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        choices=ROOM_STATUS,
        initial='available',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Room
        fields = [
            'room_number', 'room_type', 'floor', 'price_per_night',
            'capacity', 'description', 'image', 'status'
        ]
    
    def clean_room_number(self):
        """Validate room number is unique."""
        room_number = self.cleaned_data.get('room_number')
        # Exclude current instance when editing
        if self.instance.pk:
            if Room.objects.filter(room_number=room_number).exclude(
                pk=self.instance.pk
            ).exists():
                raise forms.ValidationError('This room number already exists.')
        else:
            if Room.objects.filter(room_number=room_number).exists():
                raise forms.ValidationError('This room number already exists.')
        return room_number


class RoomSearchForm(forms.Form):
    """Form for searching available rooms."""
    
    check_in = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    check_out = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    room_type = forms.ChoiceField(
        choices=[('', 'All Room Types')] + list(ROOM_TYPES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max price in TZS'
        })
    )
    
    def clean(self):
        """Validate check-in and check-out dates."""
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        
        if check_in and check_out:
            if check_in >= check_out:
                raise forms.ValidationError(
                    'Check-out date must be after check-in date.'
                )
            
            from django.utils import timezone
            if check_in < timezone.now().date():
                raise forms.ValidationError(
                    'Check-in date cannot be in the past.'
                )
        
        return cleaned_data