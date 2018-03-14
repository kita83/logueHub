from django import forms
from . import models
from django.conf import settings
from django.core.mail import send_mail


class SubscriptionForm(forms.Form):
    """
    購読Feedを取得する
    """
    require_url = forms.URLField(
        label='',
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': '新しいフィードURLを登録',
                'size': '70%',
                'class': 'form-control'
            }
        )
    )


class AddCollectionForm(forms.ModelForm):
    """
    登録済のコレクションリストの選択フォーム
    """
    # add_collection = forms.BooleanField(required=True)

    class Meta:
        model = models.MstCollection
        fields = ('title',)


class ContactForm(forms.Form):
    """
    問い合わせ用
    """
    name = forms.CharField(
        label='name',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    message = forms.CharField(
        label='message',
        required=True,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control'
            }
        )
    )

    # メール送信処理
    def send_email(self):
        # send email using the self.cleaned_data dictionary
        subject = self.cleaned_data['name']
        message = self.cleaned_data['message']
        # from_email = settings.EMAIL_HOST_USER
        from_email = 'kita83@outlook.com'
        to = [settings.EMAIL_HOST_USER]

        send_mail(subject, message, from_email, to)
