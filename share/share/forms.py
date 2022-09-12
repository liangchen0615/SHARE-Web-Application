from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.validators import FileExtensionValidator
from django.forms import ClearableFileInput, FileInput
from django_countries.widgets import CountrySelectWidget
from django_countries.fields import CountryField



from share.models import Profile, ReviewFile

MAX_UPLOAD_SIZE = 2500000



class LoginForm(forms.Form):
    attrs = {'class': 'form-control', 'style': "font-size: 18px;"}
    username = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'w-100 login-input', 'placeholder': "Username"}))
    password = forms.CharField(max_length=200, widget=forms.PasswordInput(attrs={'class': 'w-100 login-input', 'placeholder':"Password"}))

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        if not username:
            raise forms.ValidationError("Please enter username.")
        if not password:
            raise forms.ValidationError("Please enter password.")
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Invalid username/password")
        return cleaned_data


class RegisterForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'w-100 login-input', 'placeholder': "Username"}))
    password = forms.CharField(max_length=200, widget=forms.PasswordInput(attrs={'class': 'w-100 login-input','placeholder':"Password"}))
    confirm_password = forms.CharField(max_length=200, widget=forms.PasswordInput(attrs={'class': 'w-100 login-input', 'placeholder':"Confirm Password"}))
    email = forms.CharField(max_length=32, widget=forms.TextInput(attrs={'class': 'w-100 login-input', 'placeholder':"E-mail"}))
    first_name = forms.CharField(max_length=20,widget=forms.TextInput(attrs={'class': 'w-100 login-input', 'placeholder':"First Name"}))
    last_name = forms.CharField(max_length=20,widget=forms.TextInput(attrs={'class': 'w-100 login-input', 'placeholder':"Last Name"}))

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if not password:
            raise forms.ValidationError("Please enter password.")
        if not confirm_password:
            raise forms.ValidationError("Please confirm password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords did not match.")
        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")
        return username


class SearchForm(forms.Form):
    searchTerm = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class':'form-control me-2'}))

class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ('bio_text', 'picture')
        widgets = {
            'bio_text': forms.Textarea(attrs={'id': 'id_bio_input_text', 'rows': '3'}),
            'picture': forms.FileInput(attrs={'id': 'id_profile_picture'})
        }
        labels = {
            'bio_text': "",
            'picture': 'Upload image'
        }

    def clean_picture(self):
        picture = self.cleaned_data['picture']
        if not picture or not hasattr(picture, 'content_type'):
            raise forms.ValidationError('You must upload a picture')
        if not picture.content_type or not picture.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        if picture.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return picture


def file_size(value): # add this to some file where you can import it from
    limit = 50 * 1024 * 1024
    print(value)
    if value.size > limit:
        raise forms.ValidationError('File too large. Size should not exceed 2 MiB.')

class FileForm(forms.ModelForm):
    files = forms.FileField(validators=[file_size, FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'mp4'])])
    class Meta:
        model = ReviewFile
        fields = ['files']
        labels = {'files': 'Upload file'}

class AddressForm(forms.Form):
    attrs = {'class': 'form-control', 'style': "font-size: 18px;"}
    name = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'w-100 name-input', 'placeholder': "Full Name"}))
    address1 = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'w-100 add1-input', 'placeholder': "Address Line 1"}))
    address2 = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'w-100 add2-input', 'placeholder': "Address Line 2"}))
    zip_code = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'w-100 zip-input', 'placeholder': "Zip Code"}))
    city = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'w-100 city-input', 'placeholder': "City"}))
    country = CountryField(blank_label="Country").formfield(widget=CountrySelectWidget(attrs={'class': 'w-100 country-input', 'id': "country", 'placeholder': "Country"}))
    

