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
            attrs={'placeholder': '新しいフィードURLを登録'}
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
