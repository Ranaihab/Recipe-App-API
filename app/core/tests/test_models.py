from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from core import models

def create_user(**params):
    """ Create a user"""
    return get_user_model().objects.create_user(**params)

class ModelTest(TestCase):
    def test_create_user_with_email_successful(self):
        email = "test@gmail.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email = "test@gmail.com",
            password = "testpass123"
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalize(self):
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'sample123')

    def test_create_superuser(self):
        user = get_user_model().objects.create_superuser('test@gmail.com', 'sample123')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        user = create_user(email='test@fci.com', password='123456')
        recipe = models.Recipe.objects.create(user=user, title='pasta', description='sample', price=Decimal('5.50'), time_minutes=30)
        self.assertEqual(str(recipe), recipe.title)

    def test_create_Tag(self):
        user = create_user(email='test@fci.com', password='123456')
        tag= models.Tag.objects.create(user=user, name='tag')
        self.assertEqual(str(tag), tag.name)

    def test_create_Ing(self):
        user = create_user(email='test@fci.com', password='123456')
        ing= models.Ingredient.objects.create(user=user, name='tag')
        self.assertEqual(str(ing), ing.name)
