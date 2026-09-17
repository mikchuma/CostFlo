from django.contrib.auth.forms import UserCreationForm
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DeleteView, UpdateView

from expenses.forms import ExpenseForm
from expenses.models import Expense
import django.utils.timezone as timezone


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
        return super().form_valid(form)

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
