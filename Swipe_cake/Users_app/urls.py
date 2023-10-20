from django.urls import path
from .import views
from .views import ProductCategoryView



urlpatterns = [
    path("",views.Users_homebefore,name='homebefore'),
    path('User_signin',views.Users_signin,name='signin'),
    path('signin_resend_otp',views.signin_resend_otp,name='signin_resend_otp'),
    path('User_login',views.Users_login,name='login'),
    path('forgot_passwordverify',views.forgot_passwordverify,name='forgot_passwordverify'),
    path('phone_verification',views.phone_verification,name='phone_verification'),
    path('verifyotp_newpass',views.verifyotp_newpass,name='verifyotp_newpass'),
    path('new_password',views.new_password,name='new_password'),
    path('generate_otp',views.generate_otp),
    path('resend_sms',views.resend_sms,name='resend_sms'),

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
    path('product_described/<int:product_id>/',views.product_described,name='product_described'),
    path('update_quantity/<int:item_id>/',views.update_quantity,name='update_quantity'),
    path('apply_coupon_discount',views.apply_coupon_discount,name='apply_coupon_discount'),
    path('remove_coupon', views.remove_coupon, name='remove_coupon'),

    path('Product_checkout',views.Product_checkout,name='Product_checkout'),
    path('New_address',views.New_address,name='New_address'),
    path('Saved_address',views.Saved_address,name='Saved_address'),
    path('save_address',views.save_address,name='save_address'),
    path('get_saved_addresses/',views.get_saved_addresses,name='get_saved_addresses'),
    path('place_order',views.place_order,name='place_order'),
    path('place_order_success/', views.place_order_success, name='place_order_success'),
    path('view_useraccount_details',views.view_useraccount_details,name='view_useraccount_details'),
    path('delete_address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('shopitems',views.shopitems,name='shopitems'),
    path('order_details/',views.order_details,name='order_details'),
    # path('delete_order/<int:order_id>/',views.delete_order, name='delete_order'),
    path('edit_address/<int:address_id>/',views.edit_address,name='edit_address'),
    path('delete_orders/', views.delete_orders, name='delete_orders'),
    path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    # path('generate_pdf/<int:order_id>/', views.generate_pdf, name='generate_pdf'),
    path('generate_pdf/<int:order_id>/', views.generate_pdf, name='generate_pdf'),

  




    path('admin/',views.Admin_login,name='adminlogin'),
    path('adminhome',views.Admin_home,name='adminhome'),
    path('adminlogout',views.Admin_logout,name='adminlogout'),
    path('adminprofile',views.Admin_profile,name='adminprofile'),
    path('Userdetails',views.Users_details,name='userdetails'),
    path('User_search',views.User_search,name='User_search'),
    path('toggle_user_attribute/<int:user_id>/<str:attribute>/', views.toggle_user_attribute, name='toggle_user_attribute'),
    path('Product_Details',views.Product_Details_all,name='products'),
    path('Product_add',views.Product_add,name='productadd'),
    path('Productupdate/<int:product_id>/',views.Product_update,name='update'),
    path('Productupdate/<int:product_id>/do_update/',views.do_update,name='do_update'),
    path('Product_delete/<int:product_id>/',views.Product_delete,name='delete'),
    path('Product_search',views.Product_search,name='Product_search'),
    path('productcategory',views.product_category_all,name='productcategory'),
    path('categoryadd',views.Category_add,name='categoryadd'),
    path('Categoryupdate/<int:category_id>/',views.Category_update,name='categoryupdate'),
    path('Do_Category_update/<int:category_id>/Do_Category_update/',views.Do_Category_update,name='DoCategory_update'),
    path('Category_delete/<int:category_id>/',views.Category_delete,name='Category_delete'),
    path('Admin_orderstatus',views.Admin_orderstatus,name='Admin_orderstatus'),
    path('update_order_status/',views.update_order_status, name='update_order_status'),
    path('Admin_couponsdisplay',views.Admin_couponsdisplay,name='Admin_couponsdisplay'),
    path('Add_coupons',views.Add_coupons,name='Add_coupons'),
    path('delete_coupons/<int:coupon_id>/',views.delete_coupons,name='delete_coupons'),
    path('Admin_productoffer',views.Admin_productoffer,name='Admin_productoffer'),
    path('productoffer_add',views.productoffer_add,name='productoffer_add'),
    path('productoffer_delete/<int:productoffer_id>/',views.productoffer_delete,name='productoffer_delete'),
    path('Admin_categoryoffer',views.Admin_categoryoffer,name='Admin_categoryoffer'),
    path('Categoryoffer_add',views.Categoryoffer_add,name='Categoryoffer_add'),
    path('categoryoffer_disable/<int:category_offer_id>/',views.categoryoffer_disable,name='categoryoffer_disable'),
    path('sales-report/', views.sales_report, name='sales_report'),
    path('download_sales_report/', views.download_sales_report, name='download_sales_report'),
    path('orderstatus_search',views.orderstatus_search,name='orderstatus_search'),
    path('category_search',views.category_search,name='category_search'),
    path('coupon_search',views.coupon_search,name='coupon_search'),
    path('home_search',views.home_search,name='home_search'),
    path('messagess',views.messagess,name='messagess'),

    



]
