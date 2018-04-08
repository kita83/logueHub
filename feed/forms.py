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
                'placeholder': '登録したいフィードのURLを入力',
                'size': '70%',
                'class': 'form-control',
            }
        )
    )


class AddCollectionForm(forms.Form):
    """
    登録済のコレクションリストの選択フォーム
    """
    add_collection = forms.ModelChoiceField(
        required=True,
        label='選択してください',
        queryset=models.MstCollection.objects.all(),
        empty_label='--------------',
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )

    new = forms.CharField(
        required=False,
        label='または',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': '新しいコレクションフォルダを追加'
            }
        )
    )


class ContactForm(forms.Form):
    """
    問い合わせ用
    """
    email = forms.EmailField(
        label='メールアドレス',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    subject = forms.CharField(
        label='件名',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    message = forms.CharField(
        label='内容',
        required=True,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control'
            }
        )
    )

    # メール送信処理
    def send_email(self):
        """
        メールを送信する
        """
        subject = self.cleaned_data['subject']
        message = self.cleaned_data['message']
        from_email = self.cleaned_data['email']
        to = [settings.EMAIL_HOST_USER]

        send_mail(subject, message, from_email, to)
