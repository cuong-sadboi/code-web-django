from django import forms
from .models import Account, UserProfile


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Nhập mật khẩu',
        'class': 'form-control',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Nhập lại mật khẩu'
    }))

    class Meta:
        model = Account
        fields = ['first_name','last_name', 'username', 'phone_number','email','password']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Nhập tên'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Nhập họ và tên đệm'
        self.fields['username'].widget.attrs['placeholder'] = 'Nhập tên đăng nhập'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Nhập số điện thoại'
        self.fields['email'].widget.attrs['placeholder'] = 'Nhập địa chỉ email'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
    
    
    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if (len(password)<6):
            raise forms.ValidationError(
                "Password is not correct"
            )

        if password != confirm_password:
            raise forms.ValidationError(
                "Password does not match!"
            )
        

class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'phone_number')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ('address_line_1', 'profile_picture',  'city', 'state', 'country')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'