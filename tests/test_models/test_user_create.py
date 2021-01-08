import pytest


@pytest.mark.django_db
def test_user_create(django_user_model):
    user = django_user_model.objects.create(
            username='someone', password='password'
            )
    assert user.username == 'someone'
