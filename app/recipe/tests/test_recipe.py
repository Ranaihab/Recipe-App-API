from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])

def create_user(email='u1@gmail.com', password='123456', name='test'):
    return get_user_model().objects.create_user(email=email, password=password, name=name)

def create_recipe(user, **params):
    """Create and return a sample recipe."""
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample description',
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


class PublicRecipeTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeTest(TestCase):
    def setUp(self):
        self.user = create_user(email='test@gmail.com', password='123456', name='name')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)


    def test_list_recipes(self):
        create_recipe(self.user)
        create_recipe(self.user)
        create_recipe(self.user)
        create_recipe(self.user)
        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by('-id')
        ser = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, ser.data)


    def test_recipe_of_user(self):
        user = create_user()
        create_recipe(self.user)
        create_recipe(user)
        res = self.client.get(RECIPES_URL)
        myRe = Recipe.objects.filter(user=self.user).order_by('-id')
        ser = RecipeSerializer(myRe, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, ser.data)


    def test_get_recipe_detail(self):
        recipe = create_recipe(user=self.user)
        recipe_url = detail_url(recipe.id)
        res = self.client.get(recipe_url)
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)


    def test_create_recipe(self):
        payload = {
            'title': 'Sample recipe title',
            'time_minutes': 22,
            'price': Decimal('5.25'),
            'description': 'Sample description',
            'user': self.user,
        }
        res = self.client.post(RECIPES_URL, payload)
        recipe = Recipe.objects.get(id=res.data['id'])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for k, v in payload.items():
           self.assertEqual(v, getattr(recipe, k))


    def test_create_new_tag(self):
        payload = {
            'title': 'Thai Prawn Curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'tags': [{'name': 'Thai'}, {'name': 'Dinner'}],
        }

        res = self.client.post(RECIPES_URL, payload, format='json')
        recipe = Recipe.objects.filter(user=self.user)[0]
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            self.assertTrue(recipe.tags.filter(name=tag['name'], user=self.user).exists())


    def test_create_recipe_with_existing_tags(self):
        tag_indian = Tag.objects.create(user=self.user, name='Indian')
        payload = {
            'title': 'Pongal',
            'time_minutes': 60,
            'price': Decimal('4.50'),
            'tags': [{'name': 'Indian'}, {'name': 'Breakfast'}],
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_indian, recipe.tags.all())
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)


    def test_create_new_ing(self):
        payload = {
            'title': 'Thai Prawn Curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'ingredients': [{'name': 'Thai'}, {'name': 'Dinner'}],
        }

        res = self.client.post(RECIPES_URL, payload, format='json')
        recipe = Recipe.objects.filter(user=self.user)[0]
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(recipe.ingredients.count(), 2)
        for tag in payload['ingredients']:
            self.assertTrue(recipe.ingredients.filter(name=tag['name'], user=self.user).exists())


    def test_create_recipe_with_existing_ings(self):
        tag_indian = Ingredient.objects.create(user=self.user, name='Indian')
        payload = {
            'title': 'Pongal',
            'time_minutes': 60,
            'price': Decimal('4.50'),
            'ingredients': [{'name': 'Indian'}, {'name': 'Breakfast'}],
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(tag_indian, recipe.ingredients.all())
        for tag in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)


