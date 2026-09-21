from django.db import models
from django.conf import settings


class Group(models.Model):
    name = models.CharField(max_length=50)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL)

    def __str__(self):
        return f'{self.name}'

class Expense(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    category = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    date = models.DateField()
    group = models.ForeignKey(Group,on_delete=models.CASCADE,null=True,blank=True)

    def __str__(self):
        return f'{self.amount} zł - {self.category} ({self.user})'

class ExpenseShare(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    expense = models.ForeignKey(Expense,on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    paid = models.BooleanField(default=False)
