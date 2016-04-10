from django.contrib.auth.models import User
from django.db import models
from django import forms
from blog.models import UserProfile
from captcha.fields import CaptchaField

class UserForm(forms.ModelForm):
    password = forms.CharField(label='password', widget=forms.PasswordInput())
    repassword = forms.CharField(label='Confirm password', widget=forms.PasswordInput())
    captcha = CaptchaField()

    def clean(self):
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('repassword')

        if password1 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")

        return self.cleaned_data

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password','repassword')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('image',)




#ForgetPassword Part -->shrouk(classes : forgetPassForm ,confirmPassForm)
class forgetPassForm(forms.Form):
	username = forms.CharField(widget=forms.TextInput(attrs=dict(required=True,placeholder="Plz Enter Your Username...")))
	email = forms.EmailField(widget=forms.TextInput(attrs=dict(required=True,placeholder="Plz Enter Your Mail...")))
 
class confirmPassForm(forms.Form):
	code = forms.CharField(widget=forms.TextInput(attrs=dict(required=True,max_length=10,placeholder="Plz Confirmation Code...")))
 
class resetPassForm(forms.Form):
	password = forms.CharField(label='Password',widget=forms.PasswordInput(attrs=dict(required=True,placeholder="Plz Enter Your Password...")))
	confirmPassword = forms.CharField(label='Confirm Password',widget=forms.PasswordInput(attrs=dict(required=True,placeholder="Plz Enter Your Password Again...")))
 
        