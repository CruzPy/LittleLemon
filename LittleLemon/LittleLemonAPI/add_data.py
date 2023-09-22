from .models import MenuItem, Category
import os
import django

# Set the Django settings module

# Initialize Django
django.setup()

# Create Category instances
category1 = Category.objects.create(slug='appetizers', title='Appetizers')
category2 = Category.objects.create(slug='entrees', title='Entrees')
category3 = Category.objects.create(slug='desserts', title='Desserts')

# Create MenuItem instances
menu_item1 = MenuItem.objects.create(
    title='Lemon Garlic Shrimp',
    price=12.99,
    featured=True,
    category=category1
)

menu_item2 = MenuItem.objects.create(
    title='Grilled Lemon Chicken',
    price=15.99,
    featured=True,
    category=category2
)

menu_item3 = MenuItem.objects.create(
    title='Lemon Sorbet',
    price=6.99,
    featured=True,
    category=category3
)

menu_item4 = MenuItem.objects.create(
    title='Lemonade',
    price=3.49,
    featured=False,
    category=category1
)

menu_item5 = MenuItem.objects.create(
    title='Lemon Cheesecake',
    price=7.99,
    featured=False,
    category=category3
)
