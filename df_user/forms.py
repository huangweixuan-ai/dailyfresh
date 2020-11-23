from django import forms
from df_user.models import UserInfo
from django.core.exceptions import ValidationError

class UserForm(forms.ModelForm):
    repwd = forms.CharField(max_length=40, widget=forms.PasswordInput(attrs={'id': 'cpwd'}))
    class Meta:
        model = UserInfo
        fields = ['uname', 'upwd', 'uemail']

    uname = forms.CharField(widget=forms.TextInput(attrs={'id': 'user_name'}))
    upwd = forms.CharField(widget=forms.PasswordInput(attrs={'id': 'pwd'}))
    uemail = forms.CharField(widget=forms.EmailInput(attrs={'id': 'email'}))
    def clean(self):
        if self.cleaned_data.get('upwd') != self.cleaned_data.get('repwd'):
            self.add_error("repwd", ValidationError("两次密码不一样"))
        else:
            return self.cleaned_data
