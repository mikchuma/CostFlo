from django.contrib.auth.forms import UserCreationForm
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DeleteView, UpdateView, View, TemplateView
from django.shortcuts import render, get_object_or_404, redirect
from expenses.forms import ExpenseForm, GroupForm
from expenses.models import Expense, Group, ExpenseShare
import django.utils.timezone as timezone
from .forms import AddMemberForm, ExpenseShareFormSet


class SignUpView(CreateView):
    form_class = UserCreationForm 
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class ExpenseCreateView(LoginRequiredMixin,CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    success_url = reverse_lazy('expense-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        split_type = form.cleaned_data['split_type']

        if split_type == 'EQUAL':
            if self.object.group is not None:
                members = self.object.group.members.all()
                if members.count() > 0:
                    share_amount = self.object.amount / members.count()
                    for member in members:
                        if member != self.request.user:
                            ExpenseShare.objects.create(
                                user = member,
                                expense = self.object,
                                amount = share_amount,
                            )
            return response
        elif split_type == 'CUSTOM':
            return redirect('expense-custom-split',pk=self.object.pk)

        return response

class ExpenseListView(LoginRequiredMixin,ListView):
    model = Expense
    template_name = 'expenses/expense_list.html'
    context_object_name = 'expenses'

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user).order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        time = timezone.now()
        monthly_total = Expense.objects.filter(
            user=self.request.user,
            date__year=time.year,
            date__month=time.month).aggregate(total=Sum('amount'))['total'] or 0
        by_category = Expense.objects.filter(
            user=self.request.user).values('category').annotate(total=Sum('amount'))
        context['monthly_total'] = monthly_total
        context['by_category'] = by_category
        return context

class DeleteExpense(LoginRequiredMixin,DeleteView):
    model = Expense
    success_url = reverse_lazy('expense-list')

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)


class UpdateExpense(LoginRequiredMixin,UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    success_url = reverse_lazy('expense-list')
    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class CreateGroup(LoginRequiredMixin,CreateView):
    model = Group
    form_class = GroupForm
    template_name = 'expenses/group_form.html'
    success_url = reverse_lazy('expense-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.members.add(self.request.user)
        return response

class GroupListView(LoginRequiredMixin,ListView):
    model = Group
    template_name = 'expenses/group_list.html'
    context_object_name = 'groups'

    def get_queryset(self):
        return Group.objects.filter(members=self.request.user)

class AddMemberToGroup(LoginRequiredMixin,View):
    def get(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        form = AddMemberForm()
        return render(request, 'expenses/add_member_to_group.html', {'form': form, 'group': group})
    def post(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        form = AddMemberForm(request.POST)
        if form.is_valid():
            selected_member = form.cleaned_data['user']
            group.members.add(selected_member)
            return redirect('expense-list')
        return render(request, 'expenses/add_member_to_group.html', {'form': form, 'group': group})

class ExpenseShareView(LoginRequiredMixin,ListView):
    model = ExpenseShare
    template_name = 'expenses/expenseshare_list.html'
    context_object_name = 'expenses_shares'

    def get_queryset(self):
        url_pk = self.kwargs.get('pk')
        return ExpenseShare.objects.filter(expense__group_id=url_pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url_pk = self.kwargs.get('pk')
        context['total_unpaid'] = self.get_queryset().filter(paid=False).aggregate(total=Sum('amount'))['total'] or 0
        expenses = Expense.objects.filter(group_id=url_pk)
        context['expenses_with_shares'] = [
            {'expense': expense, 'shares': expense.expenseshare_set.all()}
            for expense in expenses
        ]
        unpaid_share = self.get_queryset().filter(paid=False)
        balances = {}
        for share in unpaid_share:
            debtor = share.user
            creditor = share.expense.user
            if debtor == creditor:
                continue
            key = (debtor, creditor)
            balances[key] = balances.get(key, 0) + share.amount
        net_balances={}
        for (debtor, creditor), amount in list(balances.items()):
            reverse_key = (creditor, debtor)
            key = (debtor, creditor)
            if reverse_key in balances:
                reverse_amount = balances[reverse_key]
                if amount > reverse_amount:
                    net_balances[key] = amount - reverse_amount
                elif reverse_amount > amount:
                    net_balances[reverse_key] = reverse_amount - amount
                del balances[reverse_key]
                del balances[key]
            else:
                net_balances[key] = amount
                del balances[key]
        context['net_balances'] = net_balances

        return context

class PayForShareDiff(LoginRequiredMixin,View):
    def post(self,request,group_pk,debtor_pk,creditor_pk):
        shares_to_settle = ExpenseShare.objects.filter(
            expense__group_id=group_pk,
            user_id=debtor_pk,
            expense__user_id=creditor_pk,
            paid = False
        )
        shares_to_settle.update(paid=True)
        return redirect('group-balance',pk=group_pk)

class DashBoardView(LoginRequiredMixin,TemplateView):
    template_name = 'expenses/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['my_debts'] = ExpenseShare.objects.filter(user=self.request.user,paid=False)
        context['others_debts'] = ExpenseShare.objects.filter(expense__user=self.request.user,paid=False)
        my_debts_total = context['my_debts'].aggregate(total=Sum('amount'))['total'] or 0
        others_debts_total = context['others_debts'].aggregate(total=Sum('amount'))['total'] or 0

        balance = others_debts_total - my_debts_total
        context['my_debts_total'] = my_debts_total
        context['others_debts_total'] = others_debts_total
        context['balance'] = balance

        return context


class ExpenseCustomSplitView(LoginRequiredMixin,TemplateView):
    template_name = 'expenses/custom_split.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        expense = get_object_or_404(Expense,pk=self.kwargs.get('pk'))
        group = expense.group
        initial_data = []

        if group:
            for member in group.members.all():
                initial_data.append({'user':member})
        context['expense'] = expense
        ExpenseShareFormSet.extra = len(initial_data)

        formset = ExpenseShareFormSet(instance=expense,initial = initial_data,form_kwargs={'group':group})
        context['formset'] = formset
        return context

    def post(self, request, *args, **kwargs):
        expense = get_object_or_404(Expense,pk=self.kwargs.get('pk'))
        group = expense.group
        formset = ExpenseShareFormSet(request.POST, instance=expense, form_kwargs={'group':group})
        if formset.is_valid():
            selected_users = []
            total_sum = 0
            error = None
            for form in formset.forms:
                if form.cleaned_data and not form.cleaned_data.get('DELETE',False):
                    user = form.cleaned_data.get('user')
                    amount = form.cleaned_data.get('amount',0)

                    if user in selected_users:
                        error = f"Błąd: Użytkownik {user.username} został wybrany więcej niż raz! Każda osoba może wystąpić w podziale tylko raz."
                        break
                    selected_users.append(user)
                    total_sum += amount

            if not error and total_sum != expense.amount:
                error = f"Błąd: Wpisane kwoty dają łącznie {total_sum} zł, a wydatek wynosi {expense.amount} zł! Popraw wartości."
            if not error:
                formset.save()
                return redirect('dashboard')

            context = self.get_context_data()
            context['formset'] = formset
            context['error'] = error
            return self.render_to_response(context)

        context = self.get_context_data()
        context['formset'] = formset
        return self.render_to_response(context)