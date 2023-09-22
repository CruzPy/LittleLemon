from django.urls import path
from . import views

from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # Register for new account:                     #11: POST--> 'http://localhost:8000/auth/users/' -username -password -email (optional)
    path('api-token-auth/', obtain_auth_token),     #5,12: POST -username -password
    
    # Must be authenticated for actions below (Ideal: Token)
    path('menu-items/', views.MenuItems),                           #13,14,15,16,17: GET # Try '?category=Dessert' or '?page=2'
    path('menu-items/<int:id>/', views.ViewMenuItem),               # GET
    path('view-orders/', views.ViewOrders),                         #21 GET
    
    # Admin actions
    # Access all users group: GET--> http://localhost:8000/auth/users -token
    path('managers-mod/', views.AddDeleteManagers),                 #1: POST/DELETE -username
    path('managers-view/', views.Managers),                         #2: GET
    path('menuitem-add/', views.AddMenuItem),                       #3: POST -title -price -featured -category (must exist) #15,17 add to end of URL --> '?category=Appetizer'
    path('category-add/', views.AddCategory),                       #4: POST -slug -title
    
    # Customer Actions
    path('cart-add/<int:id>/', views.AddItemToCart),                #18 GET -quantity or DELETE -none
    path('cart-view/', views.ViewCart),                             #19 GET
    path('cart-order/', views.PlaceCartOrder),                      #20 GET
    
    # Manager Actions
    path('update-featured/<int:id>/', views.UpdateFeatured),        #6: GET
    path('deliverycrew-mod/', views.AddDeleteDeliveryCrew),         #7: POST -username
    path('order-assign/<int:id>', views.AssignOrder),               #8: POST -username
    
    # Delivery Actions
    path('order-pending/', views.PendingOrders),                    #9: GET
    path('order-delivered/<int:id>', views.OrderDelivered),         #10: POST
]