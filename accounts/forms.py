from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Enter your email"}

    ),
)
    
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter a Username"}

    ),

)
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Enter password"}

    ),

)
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Conform password"}

    ),
)
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields =  (
            "username",
            "email",

        )

        def clean_email(self):
            email = self.cleaned_data.get("email")
            if User.objetcs.filter(email=email).exists():
                raise forms.ValidationError("an account with this email is already exists.")
            return email
        

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Username"}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "forms-control", "placeholder": "Password"}
        )
    )

