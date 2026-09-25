from django import forms
from django.forms import inlineformset_factory
from expenses.models import Expense, Group, ExpenseShare
from django.contrib.auth.models import User


SPLIT_CHOICES = [
    ('EQUAL','Podziel równo'),
    ('CUSTOM',"Podział niestandardowy")
]

class ExpenseForm(forms.ModelForm):
    split_type = forms.ChoiceField(
        choices=SPLIT_CHOICES,
        widget=forms.RadioSelect,
        initial='EQUAL',
        label = "Sposób udziału"
    )

    class Meta:
        model = Expense
        fields = ['amount', 'category','description','date','group','split_type']

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

class ExpenseShareForm(forms.ModelForm):
    class Meta:
        model = ExpenseShare
        fields = ['user','amount']

    def __init__(self, *args, group=None,**kwargs):
        super().__init__(*args, **kwargs)
        if group is not None:
            self.fields['user'].queryset = group.members.all()
ExpenseShareFormSet = inlineformset_factory(
    Expense,
    ExpenseShare,
    form=ExpenseShareForm,
    extra=1,
    can_delete=True
)