from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Recipe, Ingredient

from recipe.serializers import IngredientSerializer


Ingredients_URL = reverse('recipe:ingredient-list')

def detail_url(Ingredient_id):
    """Create and return a tag detail url."""
    return reverse('recipe:ingredient-detail', args=[Ingredient_id])


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(Ingredients_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)



class PrivateIngredientTest(TestCase):
    def setUp(self):
        self.user = create_user(email='test@gmail.com', password='123456')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)


    def test_list_Ingredient(self):
        Ingredient.objects.create(user=self.user, name='1')
        Ingredient.objects.create(user=self.user, name='2')
        Ingredient.objects.create(user=self.user, name='3')
        res = self.client.get(Ingredients_URL)
        ser = IngredientSerializer(Ingredient.objects.all().order_by('-name'), many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, ser.data)


    def test_Ingredient_user(self):
        user = create_user()
        Ingredient.objects.create(user=self.user, name='1')
        Ingredient.objects.create(user=user, name='2')
        res = self.client.get(Ingredients_URL)
        ser = IngredientSerializer(Ingredient.objects.filter(user=self.user).order_by('-name'), many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, ser.data)


    def test_update_ing(self):
        ing = Ingredient.objects.create(user=self.user, name='1')
        payload = {'name': '2'}
        url = detail_url(ing.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ing.refresh_from_db()
        self.assertEqual(ing.name, payload['name'])


    def test_delete(self):
        i = Ingredient.objects.create(user=self.user, name='1')
        url = detail_url(i.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        all = Ingredient.objects.filter(user=self.user)
        self.assertFalse(all.exists())