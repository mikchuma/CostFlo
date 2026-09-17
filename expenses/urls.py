from django.urls import path
from expenses.views import ExpenseCreateView, ExpenseListView, UpdateExpense, DeleteExpense

urlpatterns = [
    path('add/', ExpenseCreateView.as_view(),name = 'expense-add'),
    path('', ExpenseListView.as_view(),name = 'expense-list'),
    path('<int:pk>/edit/',UpdateExpense.as_view(),name = 'expense-edit'),
    path('<int:pk>/delete/',DeleteExpense.as_view(),name = 'expense-delete'),
]