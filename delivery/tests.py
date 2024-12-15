
from django.test import TestCase
from main.models import Category, Item, MenuList, MenuItemQuantity

class MenuListTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.item = Item.objects.create(
            category=self.category,
            name="Test Item",
            description="Test Description",
            price=10.99,
            is_active=True
        )
        self.menu = MenuList.objects.create(
            name="Test Menu",
            is_active=True
        )
        self.menu_item = MenuItemQuantity.objects.create(
            menu=self.menu,
            item=self.item,
            quantity=2
        )

    def test_menu_creation(self):
        self.assertEqual(self.menu.name, "Test Menu")
        self.assertTrue(self.menu.is_active)
        self.assertEqual(str(self.menu), "Test Menu")

    def test_menu_item_quantity(self):
        self.assertEqual(self.menu_item.quantity, 2)
        self.assertEqual(str(self.menu_item), "Test Menu - Test Item (Qty: 2)")
