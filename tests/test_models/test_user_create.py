import pytest
from apps.visualizer.models import User


@pytest.mark.django_db
def test_new_user():
    User.objects.create(username="someone", password="something")
