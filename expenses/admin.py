from django.contrib import admin

from expenses.models import Expense, Group

admin.site.register(Expense)
admin.site.register(Group)
