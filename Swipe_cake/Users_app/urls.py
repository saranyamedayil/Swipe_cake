from django.urls import path
from .import views
from .views import ProductCategoryView



urlpatterns = [
    path("",views.Users_homebefore,name='homebefore'),
    path('User_signin',views.Users_signin,name='signin'),
    path('User_login',views.Users_login,name='login'),
    path('User_homeafter',views.Users_homeafter,name='homeafter'),
    path('logout',views.Users_logout,name='logout'),
    path('sentotp',views.sent_otp,name='sentotp'),
    path('verifyotp',views.verify_otp,name='verifyotp'),
    path('products/<str:category_name>/', views.ProductCategoryView.as_view(), name='product_category'),
    path('products/category/<str:category_name>/', ProductCategoryView.as_view(), name='product_category'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('view_cart/', views.view_cart, name='view_cart'),
    path('delete_from_cart/<int:item_id>/', views.delete_from_cart, name='delete_from_cart'),
    path('Users_wishlist/<int:product_id>/',views.Users_wishlist,name='Users_wishlist'),
    path('View_userswishlist',views.View_userswishlist,name='View_userswishlist'),
    path('delete_from_wishlist/<int:item_id>/', views.delete_from_wishlist, name='delete_from_wishlist'),
    path('about',views.about,name='about'),
    path('contact',views.contact,name='contact'),
    path('calculate_cart_total',views.calculate_cart_total),    


    # path('addtocart',views.addtocart,name='addtocart'),




    path('admin/',views.Admin_login,name='adminlogin'),
    path('adminhome',views.Admin_home,name='adminhome'),
    path('adminlogout',views.Admin_logout,name='adminlogout'),
    path('adminprofile',views.Admin_profile,name='adminprofile'),
    path('Userdetails',views.Users_details,name='userdetails'),
    path('toggle_user_attribute/<int:user_id>/<str:attribute>/', views.toggle_user_attribute, name='toggle_user_attribute'),
    path('Product_Details',views.Product_Details_all,name='products'),
    path('Product_add',views.Product_add,name='productadd'),
    path('Productupdate/<int:product_id>/',views.Product_update,name='update'),
    path('Productupdate/<int:product_id>/do_update/',views.do_update,name='do_update'),
    path('Product_delete/<int:product_id>/',views.Product_delete,name='delete'),
    path('productcategory',views.product_category_all,name='productcategory'),
    path('categoryadd',views.Category_add,name='categoryadd'),
    path('Categoryupdate/<int:category_id>/',views.Category_update,name='categoryupdate'),
    path('Do_Category_update/<int:category_id>/Do_Category_update/',views.Do_Category_update,name='DoCategory_update'),
    path('Category_delete/<int:category_id>/',views.Category_delete,name='Category_delete'),
   



]
