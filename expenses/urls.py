from django.urls import path
from expenses.views import ExpenseCreateView, ExpenseListView, UpdateExpense, DeleteExpense, CreateGroup, GroupListView, \
    AddMemberToGroup, ExpenseShareView, PayForExpense

urlpatterns = [
    path('add/', ExpenseCreateView.as_view(),name = 'expense-add'),
    path('', ExpenseListView.as_view(),name = 'expense-list'),
    path('<int:pk>/edit/',UpdateExpense.as_view(),name = 'expense-edit'),
    path('<int:pk>/delete/',DeleteExpense.as_view(),name = 'expense-delete'),
    path('add/group/', CreateGroup.as_view(),name = 'group-add'),
    path('group/',GroupListView.as_view(),name = 'group-list'),
    path('group/<int:pk>/add-member/',AddMemberToGroup.as_view(),name = 'add-member-to-group'),
    path('group/<int:pk>/details/',ExpenseShareView.as_view(),name = 'group-balance'),
    path('share/<int:pk>/',PayForExpense.as_view(),name = 'share-pay'),
]