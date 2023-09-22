from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import UserSerializer, CategorySerializer, MenuItemSerializer, CartSerializer, OrderSerializer, OrderItemSerializer

from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User, Group
from datetime import datetime
from rest_framework.pagination import PageNumberPagination

# Create your views here.
@api_view()
@permission_classes([IsAuthenticated])
def ViewMenuItem(request, id):
    item = get_object_or_404(MenuItem,pk=id)
    serialized_item = MenuItemSerializer(item)
    return Response(serialized_item.data)

@api_view(['GET','DELETE'])
@permission_classes([IsAuthenticated])
def AddItemToCart(request, id):
    # Check if customer is making api call
    if request.user.groups.filter(name='Customer').exists():
        # Retrieve the user making the API call
        user = request.user
        
        # Get menuitem from id    
        menuitem = get_object_or_404(MenuItem,pk=id)
        
        if(request.method=='GET'):
            # Retrieve the QUANTITY of the menuitem from user's HTTP request
            quantity = request.data['quantity']
            # Create model object and map data to it
            NewCartItem = Cart(user=user, menuitem=menuitem, quantity=quantity, unit_price=menuitem.price, price=float(menuitem.price)*float(quantity))
            NewCartItem.save()
            return Response({'message':f'Successfully added {quantity}x {menuitem.title} to cart'})
        
        elif(request.method=='DELETE'):
            cart = get_object_or_404(Cart, menuitem=menuitem)
            cart.delete()
            return Response({'message':f'Successfully deleted {menuitem.title} from your cart'})
            
        else:
            return Response({'message':f'Only customers can add menuitems to cart'})

@api_view()
@permission_classes([IsAuthenticated])
def ViewCart(request):
    # Check if customer is making api call
    if request.user.groups.filter(name='Customer').exists():
        # Retrieve the user making the API call
        user = request.user
        # Retrieve queryset
        cart = Cart.objects.filter(user=user)
        # Serialize to JSON
        serialized = CartSerializer(cart, many=True)
        # Return data
        return Response(serialized.data)

@api_view()
@permission_classes([IsAuthenticated])
def PlaceCartOrder(request):
    # Check if customer is making api call
    if request.user.groups.filter(name='Customer').exists():
        # Retrieve the user making the API call
        user = request.user
        # Retrieve queryset
        cart = Cart.objects.filter(user=user)
        if not cart:
            return Response({'message':'Cart is empty'})

        for each in cart:
            NewOrder = OrderItem(user=each.user, menuitem=each.menuitem, quantity=each.quantity, unit_price=each.price, price=float(each.price)*float(each.quantity))
            NewOrder.save() # Create order object
            each.delete() # Delete cart item instance
        return Response({'message':'Order placed!'})
      
@api_view()
@permission_classes([IsAuthenticated])
def ViewOrders(request):
    # Retrieve the user making the API call
    user = request.user
    
    if request.user.groups.filter(name='Customer').exists():
    # If customer is making API call show only their orders
        orders = OrderItem.objects.filter(user=user)   
        
    elif request.user.groups.filter(name='Manager').exists():
    # Else if manager is making the call, show all orders
        orders = OrderItem.objects.all()
        
    # Serialize and show data
    serialized = OrderItemSerializer(orders, many=True)   
    return Response(serialized.data)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AssignOrder(request, id):
    if request.user.groups.filter(name='Manager').exists():
        # Grab order by id 
        order = OrderItem.objects.filter(pk=id)
        # Calculate order total
        total = 0
        for each in order:
            total += each.price

        # Create Order object and assign 'delivery_crew' member
        delivery_crew = User.objects.get(username=request.data['username'])
        if (delivery_crew.groups.filter(name='Delivery').exists()):
            # Create new orders and assign delivery crew
            assigned_order = Order(order=OrderItem.objects.get(pk=id), delivery_crew=delivery_crew, total=total, date=datetime.today().strftime("%Y-%m-%d"))    
            assigned_order.save()
            
            for each in order:
                order.delete()
                
            return Response({'message':f'Successfully assigned order to {delivery_crew}'})
        else:
            return Response({'message':f'Unauthorized'})
       
@api_view()
@permission_classes([IsAuthenticated])
def PendingOrders(request):
    user = request.user
    if request.user.groups.filter(name='Delivery').exists():
        order = Order.objects.filter(delivery_crew=user)
    if request.user.groups.filter(name='Manager').exists():
        order = Order.objects.all()
        
    serialized = OrderSerializer(order, many=True)
    return Response(serialized.data)
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def OrderDelivered(request,id):
    user = request.user
    if request.user.groups.filter(name='Delivery').exists():
        order = Order.objects.get(pk=id)
        order.status = True
        order.save()
        return Response({'message':'Order delivered successfully recorded'})
    
    return Response({'message':'Unauthorized'})
        
@api_view()
@permission_classes([IsAuthenticated])
def UpdateFeatured(request, id):
    if request.user.groups.filter(name='Manager').exists():
        # If exists, retrieve existing featured item
        try:
            item = MenuItem.objects.get(featured=True)
            # Remove data from featured
            item.featured = False
            item.save()
        except:
            # No featured item exists, do nothing
            pass

        # Update new item as featured
        item = get_object_or_404(MenuItem, pk=id)
        item.featured = True
        item.save()
        return Response({'message':f'Successfully added {item.title} as featured'})
    
    else:
        return Response({'message':'Unable to perform action'}, 400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def MenuItems(request):
    items = MenuItem.objects.all().order_by('price')
    
    # Capture category if in URL
    category = request.query_params.get('category', None)
    
    if category is not None:
        # Create Category instance and use it to filter for menu items containing it - else DNE
        category_obj = Category.objects.get(title=category)
        queryset = items.filter(category=category_obj)
    else:
        queryset = items

    # Initialize the paginator
    paginator = PageNumberPagination()
    paginator.page_size = 3  # Set the desired page size here

    # Paginate the queryset
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serialized_items = MenuItemSerializer(paginated_queryset, many=True)
    
    # Return paginated response
    return paginator.get_paginated_response(serialized_items.data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def AddMenuItem(request):
    # If request is coming from admin, proceed
    try:
        # Extract data from request
        title = request.data['title']
        price = request.data['price']
        featured = request.data['featured']
        category_obj = Category.objects.get(title=request.data['category']) # Must create category instance to map as foreign key

        # Map data to model
        NewItem = MenuItem(title=title, price=price, featured=featured,category=category_obj)
        NewItem.save()
        
        return Response({'message':f'Successfully added new item {title}'})
    
    except Exception as e:
        return Response({'message':f'Error while performing operation - {e}'})

@api_view(['POST'])
@permission_classes([IsAdminUser])
def AddCategory(request):
    # If request is coming from admin, proceed
    try:
        # Extract data from request
        slug = request.data['slug']
        title = request.data['title']

        # Map data to model
        NewItem = Category(slug=slug, title=title)
        NewItem.save()
        
        return Response({'message':f'Successfully added new category {title}'})
    
    except Exception as e:
        return Response({'message':f'Error while performing operation - {e}'})

@api_view(['POST','DELETE'])
@permission_classes([IsAuthenticated])
def AddDeleteDeliveryCrew(request):
    if request.user.groups.filter(name='Manager').exists():
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            delivery_crew = Group.objects.get(name="Delivery")
            if(request.method == "POST"):
                delivery_crew.user_set.add(user)
                return Response({"message":f"Added {username} as delivery crew"})
            elif(request.method == "DELETE"):
                delivery_crew.user_set.remove(user)
                return Response({"message":f"Removed {username} as delivery crew"})
    else:
        return Response({'message':'Unauthorized Action'}, 403)
    
@api_view(['POST','DELETE'])
@permission_classes([IsAuthenticated])
def AddDeleteManagers(request):
    username = request.data['username']
    if username:
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name="Manager")
        if(request.method == "POST"):
            managers.user_set.add(user)
            return Response({"message":f"Added {username} as manager"})
        elif(request.method == "DELETE"):
            managers.user_set.remove(user)
            return Response({"message":f"Removed {username} as manager"})
    
    return Response({'message':f'Error'}, 400)

@api_view(['POST','DELETE'])
@permission_classes([IsAdminUser])
def AddManager(request):
    username = request.data['username']
    if username:
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name="Manager")
        if(request.method == "POST"):
            managers.user_set.add(user)
            return Response({"message":f"You are an admin user --> Added {username} as manager"})
        elif(request.method == "DELETE"):
            managers.user_set.remove(user)
            return Response({"message":f"You are an admin user --> Removed {username} as manager"})
    
    return Response({'message':f'Error'}, 400)

@api_view()
@permission_classes([IsAdminUser])
def Managers(request):
    managers = User.objects.filter(groups__name='Manager')
    serializer = UserSerializer(managers, many=True)
    return Response(serializer.data)