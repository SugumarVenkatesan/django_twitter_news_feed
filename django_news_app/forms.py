from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'placeholder': 'E-mail address'}))
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    username = forms.CharField(required=True)
    password1 = forms.CharField(widget=forms.PasswordInput(),required=True)
    password2 = forms.CharField(widget=forms.PasswordInput(),required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password1', 'password2')
        
    #clean email field
    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            User._default_manager.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError('duplicate email')
     
    #clean password2 field
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError("Your passwords do not match")
        return password2
    
    #modify save() method so that we can set user.is_active to False when we first create our user
    def save(self, commit=True):        
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.is_active = False # not active until he opens activation link
            user.save()
    
        return user

class PasswordResetForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'placeholder': 'E-mail address'}))
    
    class Meta:
        pass
#         model = User
#         fields = ('email')
#         
    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            User._default_manager.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError('User associated with the email does not exist')
        return email
    
class PasswordResetConfirmForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput(),required=True)
    password2 = forms.CharField(widget=forms.PasswordInput(),required=True)
    
    class Meta:
        model = User
        fields = ('password1','password2')
        
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError("Your passwords do not match")
        return password2
    
   