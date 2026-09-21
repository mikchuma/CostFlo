from django import forms

from expenses.models import Expense, Group
from django.contrib.auth.models import User


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'category','description','date','group']

    def __init__(self, *args,user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['group'].queryset = Group.objects.filter(members=user)

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']

class AddMemberForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all())