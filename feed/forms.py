from django import forms
from . import models


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
    name = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)

    # メール送信処理
    def send_email(self):
        # send email using the self.cleaned_data dictionary
        subject = self.cleaned_data['name']
        message = self.cleaned_data['message']
        from_email = settings.EMAIL_HOST_USER
        to = [settings.EMAIL_HOST_USER]

        send_mail(subject, message, from_email, to)
