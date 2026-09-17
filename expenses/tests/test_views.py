import pytest
from django.contrib.auth.models import User
from expenses.models import Expense
from django.urls import reverse
from datetime import timedelta
from django.utils import timezone

@pytest.mark.django_db
def test_user_sees_only_own_expenses(client):
    user_a = User.objects.create_user(username='user_a', password='123')
    user_b = User.objects.create_user(username='user_b', password='123')

    Expense.objects.create(user=user_a,amount=10.5,category='food',date='2026-01-01')
    Expense.objects.create(user=user_b,amount=5.5,category='sport',date='2026-01-01')

    client.login(username='user_a', password='123')
    response = client.get('/expenses/')

    assert response.status_code == 200
    assert len(response.context['expenses']) == 1

@pytest.mark.django_db
def test_user_cannot_edit_others_expenses(client):
    user_a = User.objects.create_user(username='user_a', password='123')
    user_b = User.objects.create_user(username='user_b', password='123')

    expense = Expense.objects.create(user=user_a,amount=10.5,category='food',date='2026-01-01')

    client.login(username='user_b', password='123')
    response = client.get(reverse('expense-edit',args=[expense.pk]))
    assert response.status_code == 404

@pytest.mark.django_db
def test_month_summary_only_current_expenses(client):
    user_a = User.objects.create_user(username='user_a', password='123')
    old_date = timezone.now() - timedelta(days=32)
    expense1 = Expense.objects.create(user=user_a,amount=10.5,category='food',date=timezone.now())
    expense2 = Expense.objects.create(user=user_a,amount=10.5,category='food',date=old_date)

    client.login(username='user_a', password='123')
    response = client.get(reverse('expense-list'))
    assert response.context['monthly_total'] == 10.5

@pytest.mark.django_db
def test_user_without_expenses_not_none(client):
    user_a = User.objects.create_user(username='user_a', password='123')
    client.login(username='user_a', password='123')

    response = client.get(reverse('expense-list'))
    assert response.context['monthly_total'] == 0

