from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile, Note, Flag, Claim


class UserRegistrationForm(UserCreationForm):
    """Custom user registration form with additional fields"""
    
    email = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    department = forms.CharField(max_length=100, required=False, help_text='Optional.')
    phone = forms.CharField(max_length=20, required=False, help_text='Optional.')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Create user profile
            UserProfile.objects.create(
                user=user,
                department=self.cleaned_data.get('department', ''),
                phone=self.cleaned_data.get('phone', '')
            )
        
        return user


class UserLoginForm(AuthenticationForm):
    """Custom login form with remember me functionality"""
    
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-blue-600 border-slate-300 rounded'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'mt-1 w-full h-11 rounded-lg border border-slate-300 bg-white px-3 shadow-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter your username',
            'autofocus': 'autofocus',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'w-full h-11 rounded-lg border border-slate-300 bg-white px-3 pr-10 shadow-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter your password',
            'x-ref': 'pwd',
        })


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile"""
    
    class Meta:
        model = UserProfile
        fields = ('department', 'phone')
        widgets = {
            'department': forms.TextInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
        }


class AdminUserProfileForm(forms.ModelForm):
    """Admin form for editing user profiles including role"""
    
    class Meta:
        model = UserProfile
        fields = ('role', 'department', 'phone')
        widgets = {
            'role': forms.Select(attrs={'class': 'form-input'}),
            'department': forms.TextInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
        }


class ClaimAssignmentForm(forms.ModelForm):
    """Form for assigning claims to users"""
    
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        empty_label="Unassigned",
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    
    class Meta:
        model = Claim
        fields = ('assigned_to',)


class NoteForm(forms.ModelForm):
    """Form for adding notes to claims"""
    
    class Meta:
        model = Note
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-textarea w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Enter your note here...'
            })
        }


class FlagForm(forms.ModelForm):
    """Form for flagging claims"""
    
    class Meta:
        model = Flag
        fields = ('reason',)
        widgets = {
            'reason': forms.TextInput(attrs={
                'class': 'form-input w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter flag reason...'
            })
        }
