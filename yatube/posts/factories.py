import factory
from .models import Group, User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'test_user-{n}')
    first_name = factory.Sequence(lambda n: f'Vasya-{n}')
    email = factory.Sequence(lambda n: f'vasya{n}@gmail.com')


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    title = factory.sequence(lambda n: f'Group {n}')
    slug = factory.sequence(lambda n: f'group_{n}')
    description = 'empty'
