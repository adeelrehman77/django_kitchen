
from django.test import TestCase
from .models import Category, Item
from decimal import Decimal

class ItemTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.item = Item.objects.create(
            category=self.category,
            name="Test Item",
            description="Test Description",
            price=Decimal('10.99'),
            is_active=True
        )

    def test_item_creation(self):
        self.assertEqual(self.item.name, "Test Item")
        self.assertEqual(self.item.price, Decimal('10.99'))
        self.assertTrue(self.item.is_active)
        self.assertEqual(str(self.item), "Test Item")

    def test_category_relation(self):
        self.assertEqual(self.item.category.name, "Test Category")
