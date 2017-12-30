from django import forms

class SubscribeForm(forms.Form):
    """
    購読Feedを取得する
    """
    url = forms.URLField(
        label='',
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': '新しいフィードURLを登録'}
            )
        )
