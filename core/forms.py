from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Mensajes

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class MensajeForm(forms.ModelForm):
    class Meta:
        model = Mensajes
        fields = ['contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Escribe tu mensaje aquí...'
            })
        }
