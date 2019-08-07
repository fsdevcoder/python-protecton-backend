from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Product, Tag

from product.serializers import ProductSerializer, ProductDetailSerializer


PRODUCTS_URL = reverse('product:product-list')


def detail_url(product_id):
    """Return product detail URL"""
    return reverse('product:product-detail', args=[product_id])


def sample_tag(user, name='Sample tag'):
    """Create and reutn a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_product(user, **params):
    """Create and return a sample product"""
    defaults = {
        'title': 'Sample product',
        'price': 100.00
    }
    defaults.update(params)

    return Product.objects.create(user=user, **defaults)


class PublicProductApiTests(TestCase):
    """Test unauthorized product API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authenticated is required"""
        res = self.client.get(PRODUCTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateProductApiTests(TestCase):
    """Test authenticated product API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            '4086432477',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_products(self):
        """Test retrieving a list of products"""
        sample_product(user=self.user)
        sample_product(user=self.user)

        res = self.client.get(PRODUCTS_URL)

        products = Product.objects.all().order_by('-id')
        serializer = ProductSerializer(products, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_products_limited_to_user(self):
        user2 = get_user_model().objects.create_user(
            '4086432478',
            'testpass2'
        )
        sample_product(user2)
        sample_product(self.user)

        res = self.client.get(PRODUCTS_URL)

        products = Product.objects.filter(user=self.user)
        serializer = ProductSerializer(products, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_product_detail(self):
        """Test viewing a product detail"""
        product = sample_product(user=self.user)
        product.tags.add(sample_tag(user=self.user))

        url = detail_url(product.id)
        res = self.client.get(url)

        serializer = ProductDetailSerializer(product)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_product(self):
        """Test creating product"""
        payload = {
            'title': 'This product',
            'price': 5.00,
        }
        res = self.client.post(PRODUCTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(product, key))

    def test_create_product_with_tags(self):
        """Test creating a product with tags"""
        tag1 = sample_tag(user=self.user, name='tag1')
        tag2 = sample_tag(user=self.user, name='tag2')
        payload = {
            'title': 'product1',
            'tags': [tag1.id, tag2.id],
            'price': 20.00
        }
        res = self.client.post(PRODUCTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(id=res.data['id'])
        tags = product.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_partial_update_product(self):
        """Test updating a product with patch"""
        product = sample_product(user=self.user)
        product.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='new tag')

        payload = {'title': 'new product', 'tags': [new_tag.id]}
        url = detail_url(product.id)
        self.client.patch(url, payload)

        product.refresh_from_db()
        self.assertEqual(product.title, payload['title'])
        tags = product.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_product(self):
        """Test updating a product with put"""
        product = sample_product(user=self.user)
        product.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'new product',
            'price': 25.00
        }
        url = detail_url(product.id)
        self.client.put(url, payload)

        product.refresh_from_db()
        self.assertEqual(product.title, payload['title'])
        self.assertEqual(product.price, payload['price'])
        tags = product.tags.all()
        self.assertEqual(len(tags), 0)

    def test_filter_products_by_tags(self):
        """Test products with specific tags"""
        product1 = sample_product(user=self.user, title='product 1')
        product2 = sample_product(user=self.user, title='product 2')
        product3 = sample_product(user=self.user, title='product 3')

        tag1 = sample_tag(user=self.user, name='tag 1')
        tag2 = sample_tag(user=self.user, name='tag 2')

        product1.tags.add(tag1)
        product2.tags.add(tag2)

        res = self.client.get(
            PRODUCTS_URL,
            {'tags': f'{tag1.id},{tag2.id}'}
        )

        serializer1 = ProductSerializer(product1)
        serializer2 = ProductSerializer(product2)
        serializer3 = ProductSerializer(product3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
