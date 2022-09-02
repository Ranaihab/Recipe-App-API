from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Recipe, Tag

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')

def detail_url(tag_id):
    """Create and return a tag detail url."""
    return reverse('recipe:tag-detail', args=[tag_id])

def create_user(email='user@example.com', password='testpass123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)



class PrivateTagTest(TestCase):
    def setUp(self):
        self.user = create_user(email='test@gmail.com', password='123456')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)


    def test_list_tag(self):
        Tag.objects.create(user=self.user, name='1')
        Tag.objects.create(user=self.user, name='2')
        Tag.objects.create(user=self.user, name='3')
        res = self.client.get(TAGS_URL)
        ser = TagSerializer(Tag.objects.all().order_by('-name'), many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, ser.data)


    def test_tag_user(self):
        user = create_user()
        Tag.objects.create(user=self.user, name='1')
        Tag.objects.create(user=user, name='2')
        res = self.client.get(TAGS_URL)
        ser = TagSerializer(Tag.objects.filter(user=self.user).order_by('-name'), many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, ser.data)

        def test_update_tag(self):
            ing = Tag.objects.create(user=self.user, name='1')
            payload = {'name': '2'}
            url = detail_url(ing.id)
            res = self.client.patch(url, payload)
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            ing.refresh_from_db()
            self.assertEqual(ing.name, payload['name'])


        def test_delete(self):
            i = Tag.objects.create(user=self.user, name='1')
            url = detail_url(i.id)
            res = self.client.delete(url)
            self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
            all = Tag.objects.filter(user=self.user)
            self.assertFalse(all.exists())