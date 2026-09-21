from django.contrib.auth.forms import UserCreationForm
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DeleteView, UpdateView, View
from django.shortcuts import render, get_object_or_404, redirect
from expenses.forms import ExpenseForm, GroupForm
from expenses.models import Expense, Group, ExpenseShare
import django.utils.timezone as timezone
from .forms import AddMemberForm


class SignUpView(CreateView):
    form_class = UserCreationForm 
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class ExpenseCreateView(LoginRequiredMixin,CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    success_url = reverse_lazy('expense-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        if self.object.group is not None:
            members = self.object.group.members.all()
            share_amount = self.object.amount / members.count()
            for member in members:
                ExpenseShare.objects.create(
                    user = member,
                    expense = self.object,
                    amount = share_amount,
            )
        return response




    def get_from_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

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

    def get_from_kwargs(self):
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