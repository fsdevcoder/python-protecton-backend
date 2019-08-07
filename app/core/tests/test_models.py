from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(phone_number='4086432477', password='testpass'):
    """Create a sample user"""
    return get_user_model().objects.create_user(phone_number, password)


class ModelTests(TestCase):

    def test_create_user_with_phone_number_successful(self):
        """Test creating a new user with a phone number is successful"""
        phone_number = '4086432477'
        password = 'Testpass123'
        user = get_user_model().objects.create_user(
            phone_number=phone_number,
            password=password
        )

        self.assertEqual(user.phone_number, phone_number)
        self.assertTrue(user.check_password(password))

    def test_new_user_invalid_phone_number(self):
        """Test creating user with no phone_number raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            '4086432477',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Insurance'
        )

        self.assertEqual(str(tag), tag.name)

    def test_product_str(self):
        """Test the product string representation"""
        product = models.Product.objects.create(
            user=sample_user(),
            title='auto',
            price=20.00
        )

        self.assertEqual(str(product), product.title)

    def test_score_str(self):
        """Test the score string representation"""
        score = models.Score.objects.create(
            version='0.0',
            score_overall=1,
            score_medical=0,
            score_income=0,
            score_stuff=0,
            score_liability=0,
            score_digital=0
        )

        self.assertEqual(str(score), str(score.score_overall))
