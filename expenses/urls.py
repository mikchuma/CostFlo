from django.urls import path
from expenses.views import ExpenseCreateView, UpdateExpense, DeleteExpense, CreateGroup, GroupListView, \
    AddMemberToGroup, ExpenseShareView, PayForShareDiff, DashBoardView, ExpenseCustomSplitView

urlpatterns = [
    path('add/', ExpenseCreateView.as_view(),name = 'expense-add'),
    path('',DashBoardView.as_view(),name = 'dashboard'),
    path('<int:pk>/edit/',UpdateExpense.as_view(),name = 'expense-edit'),
    path('<int:pk>/delete/',DeleteExpense.as_view(),name = 'expense-delete'),
    path('add/group/', CreateGroup.as_view(),name = 'group-add'),
    path('group/',GroupListView.as_view(),name = 'group-list'),
    path('group/<int:pk>/add-member/',AddMemberToGroup.as_view(),name = 'add-member-to-group'),
    path('group/<int:pk>/details/',ExpenseShareView.as_view(),name = 'group-balance'),
    path('group/<int:group_pk>/settle/<int:debtor_pk>/<int:creditor_pk>/',PayForShareDiff.as_view(),name = 'pay-diff'),
    path('/expense/<int:pk>/custom-split/',ExpenseCustomSplitView.as_view(),name = 'expense-custom-split'),
]