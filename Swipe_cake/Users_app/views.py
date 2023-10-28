from django.shortcuts import render,redirect
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, HttpResponseRedirect, reverse
from .models import *
from .helpers import send_otp_phone
from django.http import JsonResponse,HttpResponseNotAllowed
import random
from django.views.generic import ListView
from decimal import Decimal
from django.db.models import Q
import razorpay
from django.conf import settings
from django.db import transaction
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
# from django.shortcuts import render_to_response
# from django.template import RequestContext




from django.utils import timezone


import uuid



def custom_404_page(request, exception):
    
    return render(request,'404.html', status=404)





# def handler404(request, exception, template_name="404.html"):
#     response = render_to_response(template_name)
#     response.status_code = 404
#     return response




# Create your views here.
def Users_homebefore(request):
    messages.error(request, 'please login your account')
    products={
        'product':Product_Details.objects.all()
    }
    return render(request, 'home_before.html', products)



@never_cache 
def Users_login(request):
    if "username"in request.session:
        return redirect(Users_homeafter)
    
    if request.method=='POST':

        username=request.POST.get('username')
        password=request.POST.get('password')

        if username == "" or password == "":
            messages.error(request,"empty form canot be validated")
            redirect('login')

        try:
            user = Custom_users.objects.get(username=username)
        except ObjectDoesNotExist:
            # messages.error(request, "You are not authorized to log in.")
            return render(request,'User_login.html')
        
        if user.password == password:

            if not user.is_superuser:
                if user.is_staff:
                    request.session["username"] = username  # if the user is saved in the session then it will redirect to home function
                   
                    return redirect(Users_homeafter)
                
                
            else:
                return render(request, 'home_before.html')
            
        else:
            messages.error(request,"invalid login credentials")
            return redirect(Users_login)
    else:
        
        return render(request,'User_login.html')
    

#>>>>>>>>>>>>>>>>>>>>>>>>>>> rendering the html page for forgot password >>>>>>>>>>>>>>>>>>
    

def forgot_passwordverify(request):

    return render(request,'Forgot_password_verify.html')


#>>>>>>>>>>>>>>>>>>> phone number verifying/ the phone number is exist in the db >>>>>>>>>>>>>>>>>>>

def phone_verification(request):

    if request.method=='POST':
        phonenumber=request.POST.get('phonenumber')


        if not phonenumber:
            messages.error(request,'phonenumber required')

        elif Custom_users.objects.filter(phonenumber=phonenumber).exists():

            otp = generate_otp()
            print(otp,'//////////////////////////////////////')
            

            # Save the OTP in the session for verification in the next step
            request.session['otp'] = otp
            request.session['phonenumber'] = phonenumber
            
            send_otp_phone(otp,phonenumber)
            ph = {'phone': phonenumber}

            return render(request,'verifyotp_newpass.html',ph)
        else:
            messages.error(request,'invalid phonenumber')
    
    return redirect(forgot_passwordverify)



#>>>>>>>>>>>>>>>>>>>>>>>>>>> sent otp will pass and verified through this function >>>>>>>>>>>>>>>>>>>>>>>>

def verifyotp_newpass(request):
    phonenumber = request.session.get('phonenumber')
    otp = request.session.get('otp')
    

    if request.method == 'POST':
        phone_otp = ''.join([request.POST.get(f'otp{i}', '') for i in range(1, 7)])  # Combine OTP digits

        if not phonenumber or not otp:
            messages.error(request, ' OTP required')
            return render(request, 'Forgot_password_verify.html')

        try:

            if otp == phone_otp:
                # OTP is valid, perform further actions like setting a session and redirecting
                user = Custom_users.objects.get(phonenumber=phonenumber)
                user.otp=phone_otp
                print(user.otp,'//////////////////////////////////')
                user.save()
                return redirect('new_password')  # Redirect to creating a new password
            else:
                messages.error(request, 'Invalid OTP')
                
                return render(request, 'verifyotp_newpass.html')

        except Custom_users.DoesNotExist:
            messages.error(request, 'Invalid phone number')

    return render(request, 'Forgot_password_verify.html')



 #>>>>>>>>>>>>>>>>>>unique number generating for otp >>>>>>>>>>>   

def generate_otp():
    return str(random.randint(100000, 999999))


#>>>>>>>>>>>>>>>>>>>>> generating a new password >>>>>>>>>>>>>>>>>>>>>>>>


def new_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confirmpassword')
        phonenumber = request.session.get('phonenumber')

        if new_password == "" or confirm_password == "":
            messages.error(request,"empty form cannot submit")

        elif new_password == confirm_password :
            try:
                
                user = Custom_users.objects.get(phonenumber=phonenumber)
                print(user,'0000000000000000000000000000')
                
            except Custom_users.DoesNotExist:
                messages.error(request, 'User not found.')

            user.password=new_password
            
            print(new_password,'///////////////////////////////////')
            user.save()
            messages.success(request, "Password reset successfully")
            return redirect('login')

        else:
            messages.error(request, 'New password and confirm password do not match.')

    return render(request, 'newpassword.html')  # Replace with the actual template name


#>>>>>>>>>>>>>>>>>>>>>> resend otp >>>>>>>>>>>>>>>>>>>>>>>>>

def resend_sms(request):
    phonenumber = request.session.get('phonenumber')

    if not phonenumber:
        messages.error(request, 'Invalid phonenumber')
        return render(request, 'verifyotp_newpass.html')

    try:
        user = Custom_users.objects.get(phonenumber=phonenumber)

        # Generate a new OTP
        new_otp = generate_otp()
        print(new_otp,'////////////////////////')

        # Update the session with the new OTP
        request.session['otp'] = new_otp

        # Save the new OTP in the user model
        user.otp = new_otp
        user.save()

        # Send the new OTP via SMS
        send_otp_phone(new_otp,phonenumber)

        messages.success(request, 'OTP resent successfully')
    except Custom_users.DoesNotExist:
        messages.error(request, 'User not found')

    return render(request, 'verifyotp_newpass.html')







# sign in user page rendering

def Users_signin(request):
  

    return render(request, "Usersignin.html")



# sign in users credentials checking, if valid then generating otp
    
def sent_otp(request):
    if request.method == 'POST':
        phonenumber = request.POST.get('phonenumber')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirmpass = request.POST.get('confirmpassword')

        if not username or not phonenumber or not password or not confirmpass:      #validating the sign in users details
            messages.error(request, "All fields are required")
        else:
            if password != confirmpass:
                messages.error(request, "Passwords NOT matching")
            elif len(phonenumber) != 10 or not phonenumber.isdigit():
                messages.error(request, "Invalid phone number")
            elif Custom_users.objects.filter(username=username).exists():
                messages.error(request, "Username already exists")
            elif Custom_users.objects.filter(phonenumber=phonenumber).exists():
                messages.error(request, "Phone number already used")
            else:
                try:
                    user = Custom_users(username=username, phonenumber=phonenumber, password=password)
                    user.save()
                    # Generate and send OTP only if the form is valid
                    otp = generate_otp()
                    
                    
                    send_otp_phone(otp,phonenumber)
                    user.password = password 
                    
                    user.save()

                    # Save user information in the session
                    request.session['phonenumber'] = phonenumber
                    request.session['otp'] = otp
                    request.session['username'] = username

                    # Send OTP via SMS or other methods here if needed

                    messages.success(request, 'OTP sent')
                    ph = {'phone': phonenumber}
                    return render(request, 'enter_otp.html', ph)
                except Exception as e:
                    messages.error(request, str(e))

    return redirect(verify_otp)



# >>>>>>>>>>>>>>>>>>>>>>>>>>>.  otp verification method >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def verify_otp(request):
    phonenumber = request.session.get('phonenumber')
    otp = request.session.get('otp')
    

    if request.method == 'POST':
        phone_otp = ''.join([request.POST.get(f'otp{i}', '') for i in range(1, 7)])  # Combine OTP digits

        if not phonenumber or not otp:
            messages.error(request, 'Phone number and OTP are required')
            return render(request, 'Usersignin.html')

        try:
            user_obj = Custom_users.objects.get(phonenumber=phonenumber)

            if otp == phone_otp:
                # OTP is valid, perform further actions like setting a session and redirecting
                user_obj.otp=phone_otp
                user_obj.save()
                request.session['username'] = user_obj.username
                return redirect('login')  # Redirect to the login page upon successful OTP verification
            else:
                messages.error(request, 'Invalid OTP')
                user_obj.delete()
                return render(request, 'enter_otp.html')

        except Custom_users.DoesNotExist:
            messages.error(request, 'Invalid phone number')

    return render(request, 'Usersignin.html')

def signin_resend_otp(request):
    phonenumber = request.session.get('phonenumber')

    if not phonenumber:
        messages.error(request, 'Invalid phonenumber')
        return render(request, 'Usersignin.html')

    try:
        # Retrieve the user from the database using the phone number
        user_obj = Custom_users.objects.get(phonenumber=phonenumber)

        # Generate a new OTP
        new_otp = generate_otp()
        print(new_otp, '////////////////////////')

        # Update the session with the new OTP
        request.session['otp'] = new_otp

        # Save the new OTP in the user model
        user_obj.otp = new_otp
        user_obj.save()

        # Send the new OTP via SMS (uncomment the line below once you have the send_otp_phone function)
        send_otp_phone(new_otp,phonenumber)

        messages.success(request, 'OTP resent successfully')
    except Custom_users.DoesNotExist:
        messages.error(request, 'User not found')

    return render(request, 'enter_otp.html')








# @never_cache
# def Users_homeafter(request):
#     context = {}

#     product = Product_Details.objects.all()
#     context['product'] = product

#      # Retrieve all categories
#     categories = Product_Category.objects.all()
#     context['categories'] = categories  # Add 'categories' to the context

#     if 'username' in request.session:
#         username = request.session.get('username')

#         if username:
#             # Get the user object associated with the username
#             user = Custom_users.objects.get(username=username)

#             cart_items = CartItem.objects.filter(user=user)

#             subtotal_dict = {}
#             total = Decimal(0)
#             cart_count = 0  # Initialize cart count

#             for item in cart_items:
#                 # Calculate the total price for each cart item
#                 item_total = item.quantity * item.product.product_price
#                 if item.product.product_category.category_name in subtotal_dict:
#                     # If it exists, add the item total to the existing subtotal
#                     subtotal_dict[item.product.product_category.category_name] += item_total
#                 else:
#                     # If it doesn't exist, create a new entry
#                     subtotal_dict[item.product.product_category.category_name] = item_total

#                 # Add item total to the total
#                 total += item_total
#                 cart_count += item.quantity
                

#             # Add 'cart_total' to the context
#             context['cart_total'] = total
#             context['cart_count'] = cart_count
#             context['username'] = username


#             return render(request, "home_after.html", context)  # Pass the context with 'cart_total'
    
#     return redirect(Users_login)
from django.core.exceptions import ObjectDoesNotExist  # Import the exception

@never_cache
def Users_homeafter(request):
    context = {}

    product = Product_Details.objects.all()
    context['product'] = product

    categories = Product_Category.objects.all()
    context['categories'] = categories

    msg=Message.objects.all()
    context['mesg']=msg

    if 'username' in request.session:
        username = request.session.get('username')
        print(username,'/////////////////////////////')

        if username:
            try:
                user = Custom_users.objects.get(username=username)  # Try to get the user

                cart_items = CartItem.objects.filter(user=user)

                subtotal_dict = {}
                total = Decimal(0)
                cart_count = 0

                for item in cart_items:
                    item_total = item.quantity * item.product.product_price
                    if item.product.product_category.category_name in subtotal_dict:
                        subtotal_dict[item.product.product_category.category_name] += item_total
                    else:
                        subtotal_dict[item.product.product_category.category_name] = item_total

                    total += item_total
                    cart_count += item.quantity

                context['cart_total'] = total
                context['cart_count'] = cart_count
                context['username'] = username

                return render(request, "home_after.html", context)

            except ObjectDoesNotExist:
                # Handle the case where the user or cart items do not exist
                return render(request, "User_login.html")
        else:
            # Handle the case where 'username' is in the session but not found
            return render(request, "User_login.html")
    else:
        return redirect(Users_login)




def Users_logout(request):
    if "username" in request.session:           #removing data saved in the session
        request.session.flush()
    return redirect(Users_homebefore)
















#>>>>>>>>>>>>>>>>>>>>>>..  custom admin panel >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.

@never_cache
def Admin_login(request):
    if "username"in request.session: 
        return redirect(Admin_home)
    if request.method == "POST":
     
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(username=username, password=password)
        if user and user.is_superuser:
            request.session["username"]=username
            auth_login(request,user)
            return redirect(Admin_home)
        else:
            messages.error(request,"invalid login")
            return redirect(Admin_login)
    else:
        
        return render(request,'Admin_login.html')
    


@never_cache
def Admin_home(request):
       
        if 'username' in request.session:
             return render(request,"admin_home.html")
        return redirect(Admin_login)

@never_cache
def Admin_logout(request):
    if "username" in request.session:
        request.session.flush()
    return redirect(Admin_login)


#.............................. admin profile.......................



def Admin_profile(request):
    superusers = User.objects.filter(is_superuser=True)
    context = {'superusers': superusers}
    return render(request,'Admin_profile.html',context)




#>>>>>>>>>>>>>>>>>>>>>>>>> user details  in admin side >>>>>>>>>>>>>>>>>>>>>>>>>>>

# def Users_details(request):
#     user={
#         'users':Custom_users.objects.all()
#     }
#     return render(request,'Users_details.html',user).
def Users_details(request):
    users = Custom_users.objects.all().order_by('-id')  # Order by 'id' in descending order
    context = {
        'users': users
    }
    return render(request, 'Users_details.html', context)




def toggle_user_attribute(request, user_id, attribute):
    user = get_object_or_404(Custom_users, id=user_id)

    # Check if the attribute is valid (is_superuser, is_staff, or is_blocked)
    if attribute not in ['is_superuser', 'is_staff', 'is_blocked']:
        return JsonResponse({'success': False, 'error': 'Invalid attribute'})

    # Toggle the attribute
    if hasattr(user, attribute):
        current_value = getattr(user, attribute)
        setattr(user, attribute, not current_value)
        user.save()

        # Prepare the response message based on the current status
        message = f"User {user.username} has been {'blocked' if not current_value else 'unblocked'}."

        return JsonResponse({'success': True, 'new_value': not current_value, 'message': message})
    else:
        return JsonResponse({'success': False, 'error': 'Attribute not found'})
    
def User_search(request):
    if 'q' in request.GET:
        q=request.GET['q']
        multiple_s=Q(Q(username__icontains=q)|Q(phonenumber__icontains=q))
        users=Custom_users.objects.filter(multiple_s)
    
    else:
        users=Custom_users.objects.all()

    user={
        'users':users
    }
    return render(request,"Users_details.html",user)


def orderstatus_search(request):
    if 'q' in request.GET:
        q = request.GET['q']
        multiple_s = Q(
            Q(user__username__icontains=q) |
            Q(order_number__icontains=q) |
            Q(orderitems__product__product_name__icontains=q) |
            Q(order_date__icontains=q) |
            Q(payment_method__icontains=q)|
            Q(status__icontains=q)

        )
        orders = Order.objects.filter(multiple_s).distinct()


    context = {
        'orders': orders
    }
    return render(request, "Admin_Orderstatus.html", context)

def category_search(request):
    if 'q' in request.GET:
        q = request.GET['q']
        multiple_s = Q(
            Q(category_name__icontains=q) 

        )

    category=Product_Category.objects.filter(multiple_s).distinct()
    context={
        'category':category
    }

    return render(request,'Product_category.html',context)


def coupon_search(request):
    if 'q' in request.GET:
        q = request.GET['q']
        multiple_s = Q(
            Q(code__icontains=q) |
            Q(discount_type__icontains=q) |
            Q(discount_value__icontains=q) 
           


        )

    coupons=Coupon.objects.filter(multiple_s).distinct()
    context={
        'coupons':coupons
    }

    return render(request,'Admin_coupons.html',context)


def home_search(request):
    if 'q' in request.GET:
        q = request.GET['q']
        multiple_s = Q(
            Q(product_name__startswith=q) |  # Fixed here
            
            Q(product_price__startswith=q)
        )
        products = Product_Details.objects.filter(multiple_s).distinct()

        context = {
            'product': products,
        }
        if not products:
            context['no_items_message'] = 'No items found for your search.'

        return render(request, 'home_after.html', context)



def messagess(request):
    messages=Message.objects.all()
   
    return render(request,'home_after.html', {'messages': messages})

# def feedback_submission(request):
#     username=request.session.get('username')

#     if request.method =='POST':
#         name=request.POST.get('name')
#         feedback=request.POST.get('feedback')

#         if name !=username:
#             messages.error(request,'submit the feedback with your username')
#             return redirect(feedback_submission)
#         elif name == '' or feedback == '':
#             messages.error(request,'fill the fields')
#             return redirect(feedback_submission)
#         else:
#             feedback=Message(message=feedback)
#             feedback.save()
#             return redirect(Users_homeafter)
from django.shortcuts import get_object_or_404

def feedback_submission(request):
    username = request.session.get('username')
    user_instance = get_object_or_404(Custom_users, username=username)  # Retrieve the user instance

    if request.method == 'POST':
        name = request.POST.get('name')
        feedback = request.POST.get('feedback')

        if name != username:
            messages.error(request, 'Submit the feedback with your username')
            return redirect(feedback_submission)
        elif name == '' or feedback == '':
            messages.error(request, 'Fill in all the fields')
            return redirect(feedback_submission)
        else:
            feedback = Message(user=user_instance, message=feedback)
            feedback.save()
            messages.success(request,'feedback submitted successfully')
            return redirect(Users_homeafter)

    return redirect(Users_homeafter)

   

#??????????????????????????????????????  products details based codes in admin side ??????????????????????????????????



def Product_Details_all(request):
    products=Product_Details.objects.all()
    
     # Specify the number of items per page
    items_per_page = 10  # You can adjust this value as needed
    
    # Create a Paginator instance
    paginator = Paginator(products, items_per_page)
    
    # Get the current page number from the request's GET parameters
    page = request.GET.get('page')
    
    try:
        # Get the corresponding page of orders
        products = paginator.get_page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver the first page.
        products = paginator.get_page(1)
    except EmptyPage:
        # If page is out of range, deliver the last page of results.
        products = paginator.get_page(paginator.num_pages)

    products ={
        'product':products
    }

    return render(request,'Product_details.html',products)

def Product_add(request):
    categories = Product_Category.objects.all()

    if request.method == 'POST':
        try:
            productname = request.POST['productname']
            category_id = request.POST['category']
            stock = request.POST['stock']
            price = request.POST['price']
            image = request.FILES['image']
            quantity = request.POST.get('quantity', 0)  # Default to 0 if not provided


             # Check if a product with the same name exists
            existing_product = None

            try:
                existing_product = Product_Details.objects.get(product_name=productname)
            except ObjectDoesNotExist:
                pass


            # Check if a product with the same name exists
            if existing_product:
               
                messages.error(request, 'A product with the same name already exists')
                
                # Update the existing product with the new data
                existing_product.product_category_id = category_id
                existing_product.product_stock = stock
                existing_product.product_price = price
                existing_product.product_image = image
                existing_product.product_quantity = quantity
                existing_product.save()
                
                return redirect(Product_Details_all)
            

            # Check if the specified category exists
            try:
                category = Product_Category.objects.get(pk=category_id)
            except Product_Category.DoesNotExist:
                messages.error(request, 'Category not found')
                return redirect(Product_Details_all)

            # Create a Product_Details instance with the correct field names
            product = Product_Details(
                product_name=productname,
                product_category=category,
                product_stock=stock,
                product_price=price,
                product_image=image,
                product_quantity=quantity  # Provide the value for product_quantity
            )
            product.save()

            return redirect(Product_Details_all)
        except Exception as e:
            # Handle other exceptions, including any unexpected errors
            messages.error(request, f'Error adding/updating product: {str(e)}')
            return redirect(Product_Details_all)

    return render(request, 'Product_Add.html', {'categories': categories})



def Product_update(request, product_id):
    prod_up = Product_Details.objects.get(product_id=product_id)
    categories = Product_Category.objects.all()
    context = {'pd_up': prod_up, 'categories': categories}
    return render(request, 'Product_edit.html', context)


     # when we click update the details should automatically fill in the form

def do_update(request, product_id):

    try:
        product = get_object_or_404(Product_Details, product_id=product_id)       #the customer users details to be fetching and store to users 

        product.product_name = request.POST.get('productname')                #updated values to be store in db
        
        # Fetch the category object based on the category name
        category_name = request.POST.get('category')
        try:
            category = Product_Category.objects.get(category_name=category_name)
        except Product_Category.DoesNotExist:
            # Handle the case where the category doesn't exist (you can create it if needed)
            category = None
        
        if category:
            product.product_category = category

        product.product_stock = request.POST.get('stock')
        product.product_price = request.POST.get('price')
        
    
        if 'image' in request.FILES:
            product.product_image = request.FILES.get('image')
            print(product.product_image)

        # Ensure 'quantity' is not None and convert it to float
        quantity = request.POST.get('quantity')
        if quantity is not None:
            product.product_quantity = float(quantity)

        product.save()                                             #the updated values to be saved then redirect to productdetails page

        return redirect(Product_Details_all)
    
    except Product_Details.DoesNotExist:
        # Handle the case where the product does not exist
        messages.error(request, 'Product not found')
        return redirect(Product_Details_all)
    
    except Product_Category.DoesNotExist:
        # Handle the case where the category specified in the form does not exist
        messages.error(request, 'Category not found')
        return redirect(Product_Details_all)

    except Exception as e:
        # Handle other exceptions, including ForeignKey constraint failure
        messages.error(request, f'Error updating product: {str(e)}')
        return redirect(Product_Details_all)
    



def Product_delete(request,product_id):
  if request.method == 'POST':
    product = get_object_or_404(Product_Details, product_id=product_id)
    product.delete()
    return redirect(Product_Details_all)
  return HttpResponseRedirect(reverse(Product_Details_all))


def Product_search(request):
    if 'q' in request.GET:
        q=request.GET['q']
        multiple_q=Q(Q(product_name__icontains=q) |Q(product_category__category_name__icontains=q)|   #to search multiple data's import 'Q'
                    Q(product_id__icontains=q))
        
        products=Product_Details.objects.filter(multiple_q)

    else:

        Product_Details.objects.all()

    product={
        'product':products
    }

    return render(request,'Product_details.html',product)




#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>product category based codes>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


def product_category_all(request):

    category ={
        'category':Product_Category.objects.all()
    }

    return render(request,'Product_category.html',category)


def Category_add(request):
    if request.method=='POST':
        Categoryname = request.POST['categoryname']
        quantity = request.POST.get('quantity', 0)  # Default to 0 if not provided

        if Categoryname == "" or quantity == "":
            messages.error(request,'fill the fields')

        
        else:

        # Create a Product_Details instance with the correct field names
            category = Product_Category(
                category_name=Categoryname,
                Category_quantity=quantity  # Provide the value for product_quantity
            )
            category.save()


            return redirect(product_category_all)
    

    return render(request,'Category_add.html')

def Category_update(request, category_id):

    cat_up = Product_Category.objects.get(category_id=category_id)                
    return render(request,'category_update.html',{'ct_up':cat_up})



def Do_Category_update(request,category_id ):
    product = get_object_or_404(Product_Category, category_id=category_id)       #the customer users details to be fetching and store to users 

    product.category_name = request.POST.get('categoryname')                #updated values to be store in db
    
    # Ensure 'quantity' is not None and convert it to float
    Category_quantity = request.POST.get('quantity')
    if Category_quantity is not None:
        product.Category_quantity= float(Category_quantity)

    product.save()                                             #the updated values to be saved then redirect to productdetails page

    return redirect(product_category_all)



def Category_delete(request,category_id):
  if request.method == 'POST':
    product = get_object_or_404(Product_Category, category_id=category_id)
    product.delete()
    return redirect(product_category_all)
  return HttpResponseRedirect(reverse(product_category_all))







#......................product arrange in category wise..................................

class ProductCategoryView(ListView):
    template_name = 'product_categorywise.html'  
    context_object_name = 'products'

    def get_queryset(self):
        # Get the category name from the URL

        category_name = self.kwargs['category_name']

        # Filter products by category name
        queryset = Product_Details.objects.filter(product_category__category_name=category_name)

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_name = self.kwargs['category_name']

        # Fetch category-wise offer
        try:
            category_offer = Category_Offer.objects.get(category__category_name=category_name,
                                                        expiration_date__gte=timezone.now().date())
            context['category_offer'] = category_offer
        except Category_Offer.DoesNotExist:
            context['category_offer'] = None

        # Calculate cart total using the calculate_cart_total function
        if 'username' in self.request.session:
            username = self.request.session.get('username')

            if username:
                user = Custom_users.objects.get(username=username)
                total,cart_count = calculate_cart_total(user)
                context['cart_total'] = total  # Add 'cart_total' to the context
                context['cart_count'] = cart_count
                
        context['username'] = username
        context['category_name'] = category_name
        return context




#>>>>>>>>>>>>>>>>>>>>>>>>>>> add to cart $ displaying & deleting >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


def add_to_cart(request, product_id):
    product = get_object_or_404(Product_Details, product_id=product_id)
    username = request.session.get('username')

    if username:
        user = Custom_users.objects.get(username=username)
        existing_cart_item = CartItem.objects.filter(user=user, product=product).first()
        
        if existing_cart_item:
            existing_cart_item.quantity += 1
            existing_cart_item.save()
        else:
            new_cart_item = CartItem(user=user, product=product, quantity=1)
            new_cart_item.save()
            messages.success(request, 'Product added to your cart')

            WishlistItem.objects.filter(user=user, product=product).delete()
        
       
        return redirect('homeafter')  # Replace 'view_cart' with the actual URL name of your cart page

def update_quantity(request, item_id):
    if request.method == 'POST':
        new_quantity = int(request.POST.get('new_quantity', 0))

        if new_quantity >= 0:
            try:
                item = CartItem.objects.get(id=item_id)
                item.quantity = new_quantity
                item.save()
                return JsonResponse({'success': True})
            except CartItem.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Item not found'})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# def check_stock_status(request, item_id):
#     try:
#         product = Product_Details.objects.get(product_id=item_id)

#         # Check if the requested quantity exceeds available stock
#         is_out_of_stock = product.product_stock <= 0
#         stock_quantity = product.product_stock

#         response_data = {
#             'is_out_of_stock': is_out_of_stock,
#             'stock_quantity': stock_quantity,
#         }
#         return JsonResponse(response_data)
#     except Product_Details.DoesNotExist:
#         return JsonResponse({'error': 'Product not found'}, status=404)

def view_cart(request):
    username = request.session.get('username')

    if username:
        user = Custom_users.objects.get(username=username)
        cart_items = CartItem.objects.filter(user=user)

        subtotal_dict = {}
        total = Decimal(0)
        cart_count = 0

        total,cart_count = calculate_cart_total(user)
      

        # # Remove the discount_amount from the session
        # if 'discount_amount' in request.session:
        #     del request.session['discount_amount']


        for item in cart_items:
            item_total = item.quantity * item.product.product_price

            category_name = item.product.product_category.category_name
            subtotal_dict[category_name] = subtotal_dict.get(category_name, 0) + item_total

            # total += item_total
        

        return render(request, 'shoping-cart.html', {'cart_items': cart_items, 'subtotal_dict': subtotal_dict, 'cart_total': total,'cart_count':cart_count,'username':username})
    else:
        messages.warning(request, 'Please log in to view your cart.')
        return redirect('login')
    






def delete_from_cart(request, item_id):
    username = request.session.get('username')
    
    if username:
        user = Custom_users.objects.get(username=username)
        cart_item = get_object_or_404(CartItem, id=item_id, user=user)
        cart_item.delete()
        messages.success(request, 'Product removed from cart')

    return redirect('view_cart')


#............................................ calculating the cart total into seperate function ...................................

def calculate_cart_total(user):
    cart_items = CartItem.objects.filter(user=user)
    total = Decimal(0)
    cart_count = 0
    

    for item in cart_items:
        # Calculate the total price for each cart item
        item_total = item.quantity * item.product.product_price
        total += item_total
        cart_count += item.quantity
    

    return total,cart_count


#???????????????????????????????????? about page ????????????????????????

def about(request):
    username = request.session.get('username')
    total = Decimal(0)  # Default total for unauthenticated users
    cart_count = 0  # Default cart count

    if username:
        # Get the user object associated with the username
        user = Custom_users.objects.get(username=username)
        total,cart_count = calculate_cart_total(user)
    
        

    return render(request, 'about.html', {'cart_total': total,'cart_count': cart_count,'username':username})



########################### contact page ??????????????????????????????

def contact(request):
    username = request.session.get('username')
    total = Decimal(0)  # Default total for unauthenticated users
    cart_count = 0  # Default cart count

    if username:
        # Get the user object associated with the username
        user = Custom_users.objects.get(username=username)
        total,cart_count = calculate_cart_total(user)

    return render(request,'contact.html',{'cart_total': total,'cart_count': cart_count,'username':username})




#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< adding products into wishlist, view and removing  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


def Users_wishlist(request,product_id): 
    username = request.session.get('username')
  
    if username:
        # Get the user object associated with the username
        user = Custom_users.objects.get(username=username)
        product = get_object_or_404(Product_Details, product_id=product_id)
       


    # Check if the user already has this product in their cart
        existing_wishlist_item = WishlistItem.objects.filter(user=user, product=product).exists()

        if existing_wishlist_item:
            messages.warning(request, 'Product is already in your wishlist')

        else:
            new_wishlist_item = WishlistItem(user=user, product=product)
            new_wishlist_item.save()
            messages.success(request, 'Product added to your wishlist')
    else:
        messages.warning(request, 'Please log in to add products to your wishlist')

    return redirect(Users_homeafter)



def View_userswishlist(request):
    username = request.session.get('username')
    total = Decimal(0)  # Default total for unauthenticated users
    cart_count = 0  # Default cart count


   

    if username:
        user=Custom_users.objects.get(username=username)
        total,cart_count = calculate_cart_total(user)

        wishlist_items=WishlistItem.objects.filter(user=user)

    else:
        messages.warning(request, 'please login your account')
        return redirect(Users_login)
    

    return render(request,'User_wishlist.html',{'wishlist':wishlist_items,'cart_total': total,'cart_count': cart_count,'username':username})


def delete_from_wishlist(request, item_id):
    username = request.session.get('username')
    if username:
        # Get the user object associated with the username
        user = Custom_users.objects.get(username=username)

        
    # Get the wishlist item to delete
        wishlist_item = get_object_or_404(WishlistItem, id=item_id, user=user)

    # Delete the wishlist item
        wishlist_item.delete()
        messages.success(request,'product removed from wishlist')

    # Redirect back to the wishlist page 
    return redirect(View_userswishlist)



#>>>>>>>>>>>>>>>>>>>>>>>>>>>product described page & related product >>>>>>>>>>>>>>>>>>>>>>

def product_described(request,product_id):
    username=request.session.get('username')
    product = get_object_or_404(Product_Details, product_id=product_id)
    related_products = get_related_products(product_id)
    total = Decimal(0)  # Default total for unauthenticated users
    cart_count = 0  # Default cart count

    
    if username:
        user=Custom_users.objects.get(username=username)
        total,cart_count = calculate_cart_total(user)
        context = {
        'product': product,
        'related_products': related_products,
        'cart_total': total,
        'cart_count': cart_count,
        'username':username

    }
     # Fetch product offer
        try:
            product_offer = Product_Offer.objects.get(product=product, expiration_date__gte=timezone.now().date())
            context['product_offer'] = product_offer
        except Product_Offer.DoesNotExist:
            context['product_offer'] = None

    return render(request,'Described_Productdetails.html',context)


def get_related_products(product_id):
    # Get the product for which you want to find related products
    product = get_object_or_404(Product_Details, product_id=product_id)

    # Define criteria for related products (e.g., same category)
    related_products = Product_Details.objects.filter(
        product_category=product.product_category  # Assuming category is a ForeignKey
    ).exclude(product_id=product_id)  # Exclude the current product from the list

    # You can further refine the criteria based on your needs (e.g., matching tags)

    return related_products



#>>>>>>>>>>>>>>>>>>>>>>>>>> checkout / adding coupons >>>>>>>>>>>>>>>>>>>>>>>>



def Product_checkout(request):
    username = request.session.get('username')
    cart_count = 0
    discount_amount = 0
    applied_coupon = None
    Ct_discount_amount = 0
    pddiscount_amount = 0
    cart_total = 0 

    if username:
        user = Custom_users.objects.get(username=username)
        cart_items = CartItem.objects.filter(user=user)
        subtotal_dict = {}
        total, cart_count = calculate_cart_total(user)  # Implement calculate_cart_total
        

        # Initialize the total_float as the initial total
        total_float = Decimal(str(total))

        if request.method == 'POST':
            coupon_code = request.POST.get('coupon_code')

            try:
                coupon = Coupon.objects.get(code=coupon_code)

                if coupon.is_valid() and total_float > 500:
                    discount_amount = apply_coupon_discount(coupon, total_float)
                    total_float -= discount_amount
                    applied_coupon = coupon
                    request.session['coupon_code'] = coupon.code
                    request.session['total_float'] = float(total_float)
                    messages.success(request, 'Coupon applied successfully.')
                else:
                    messages.error(request, 'Invalid coupon or order less than 500.')

            except Coupon.DoesNotExist:
                messages.error(request, 'Invalid coupon code')

        
        displayed_categories = set()

        for item in cart_items:
            category = item.product.product_category

            try:
                category_offer = Category_Offer.objects.get(category=category, expiration_date__gte=timezone.now().date(), is_active=True)
                if category_offer:
                    if item.product.product_category.category_name not in displayed_categories:
                        displayed_categories.add(item.product.product_category.category_name)
                        item.display_category_offer = True
                    else:
                        item.display_category_offer = False

                if category_offer.offer_type == 'percentage':
                    Ct_discount_amount += (category_offer.discount_value / 100) * item.product.product_price * item.quantity
                elif category_offer.offer_type == 'fixed':
                    Ct_discount_amount += category_offer.discount_value

                item.category_offer = category_offer

            except Category_Offer.DoesNotExist:
                pass

            

            product = item.product
            try:
                product_offer = Product_Offer.objects.get(product=product, expiration_date__gte=timezone.now().date(), is_active=True)

                if product_offer.offer_type == 'percentage':
                    pddiscount_amount += product.product_price * item.quantity * (product_offer.discount_value / 100)
                elif product_offer.offer_type == 'fixed':
                    pddiscount_amount += product_offer.discount_value * item.quantity

                item.product_offer = product_offer

            except Product_Offer.DoesNotExist:
                pass

            item_total = item.quantity * item.product.product_price

            category_name = item.product.product_category.category_name
            subtotal_dict[category_name] = subtotal_dict.get(category_name, 0) + item_total

        # Deduct category-wise and product-wise offers from the total
        total_float -= Decimal(str(Ct_discount_amount))
        total_float -= Decimal(str(pddiscount_amount))
        request.session['total_float'] = float(total_float)
        coupon = Coupon.objects.all()
        cart_total = float(total_float)  # Set the cart_total value
       

    return render(request, 'product_checkout.html', {
        'cart_items': cart_items,
        'subtotal_dict': subtotal_dict,
        'cart_total': cart_total,
        'cart_count': cart_count,
        'total': total,
        'discount_amount': float(discount_amount),
        'applied_coupon': applied_coupon,
        'Ct_discount_amount': Ct_discount_amount,
        'pddiscount_amount': pddiscount_amount,
        'available_coupons': coupon,
        'username':username,
        'displayed_categories':displayed_categories
    })


#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< applying coupon discounts >>>>>>>>>>>>>>>>>>>>>>>>>>>


def apply_coupon_discount(coupon, total):
    if coupon.discount_type == 'percentage':
        discount_amount = (coupon.discount_value / 100) * total
    elif coupon.discount_type == 'fixed':
        discount_amount = min(coupon.discount_value, total)  # Ensure the discount doesn't exceed the total

    return  discount_amount

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> remove coupons >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def remove_coupon(request):
    # Remove the coupon from the session or database
    coupon_code = request.session.get('coupon_code')
    print(coupon_code,'...............................')
    if coupon_code:
        print(coupon_code)
        del request.session['coupon_code']
        messages.success(request,'coupon removed successfully')

    return redirect(Product_checkout)



#>>>>>>>>>>>>>>>>>>>>>>>> adminside coupons displaying / adding functions / delete / update >>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def Admin_couponsdisplay(request):
    coupon={
        'coupons':Coupon.objects.all()
    }

    return render(request,'Admin_coupons.html',coupon)

# def Add_coupons(request):
#       if request.method == 'POST':
#         code = request.POST.get('code')
#         discount_type = request.POST.get('discount_type')
#         discount_value = request.POST.get('discount_value')
#         expiration_date = request.POST.get('expiration_date')

#         if code == "" or discount_type == "" or discount_value == "" or expiration_date == "":
#             messages.error(request,"Empty form can't be submit")

#         # Perform necessary validation on input data before saving
#         else:
#             Coupon.objects.create(
#                 code=code,
#                 discount_type=discount_type,
#                 discount_value=discount_value,
#                 expiration_date=expiration_date
#             )

#             return redirect('Admin_couponsdisplay') 
        
#       return render(request,'Admin_couponsAdd.html')


def Add_coupons(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        discount_type = request.POST.get('discount_type')
        discount_value = request.POST.get('discount_value')
        expiration_date = request.POST.get('expiration_date')

        if code == "" or discount_type == "" or discount_value == "" or expiration_date == "":
            messages.error(request, "Empty form can't be submitted")
        else:
            discount_value = int(discount_value)

            if discount_type == 'percentage':
                # Check if the percentage discount is less than 30%
                if discount_value > 30 or discount_value < 0:
                    messages.error(request, "Percentage discount must be greaterthan 0 and lessthan 30%")
                else:
                    Coupon.objects.create(
                        code=code,
                        discount_type=discount_type,
                        discount_value=discount_value,
                        expiration_date=expiration_date
                    )
                    return redirect('Admin_couponsdisplay')
            elif discount_type == 'fixed':
                # Check if the fixed discount is less than 150
                if discount_value > 150 or discount_value < 0:
                    messages.error(request, "Fixed discount must be lessthan Rs.150 or greaterthan 0")
                else:
                    Coupon.objects.create(
                        code=code,
                        discount_type=discount_type,
                        discount_value=discount_value,
                        expiration_date=expiration_date
                    )
                    return redirect('Admin_couponsdisplay')
            else:
                messages.error(request, "Invalid discount type")

    return render(request, 'Admin_couponsAdd.html')


def delete_coupons(request,coupon_id):
     if request.method == 'POST':
        coupon = get_object_or_404(Coupon, id=coupon_id)
        coupon.delete()
        return redirect(Admin_couponsdisplay)
     return HttpResponseRedirect(reverse(Admin_couponsdisplay))
    




    

#>>>>>>>>>>>>>>>>>>>>>>> adding new address for delivering the product >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def New_address(request):
    username = request.session.get('username')
    total = Decimal(0)  # Default total for unauthenticated users
    cart_count = 0  # Default cart count


   

    if username:
        user=Custom_users.objects.get(username=username)
        total,cart_count = calculate_cart_total(user)

    return render(request,'add_address.html',{'cart_total': total,'cart_count': cart_count,'username':username})


def save_address(request):

    if request.method == 'POST':
        # Retrieve the form data
        

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        country = request.POST.get('country')
        street_address = request.POST.get('street_address')
        apartment = request.POST.get('apartment')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zipcode = request.POST.get('zipcode')
        phone = request.POST.get('phone')
        email = request.POST.get('email')

        username=request.session.get('username')
        user=Custom_users.objects.get(username=username)

        

        # Create and save the new address
        address = Users_Address(
            user=user,
            first_name=first_name,
            last_name=last_name,
            country=country,
            street_address=street_address,
            apartment=apartment,
            city=city,
            state=state,
            zipcode=zipcode,
            phone=phone,
            email=email
        )
        address.save()
        messages.success(request,'address saved successfully')

        # Redirect to a success page or any other desired page
        return redirect('Product_checkout')  # Update with the appropriate URL name

    # If the request method is not POST, render the form page
    return render(request, 'add_address.html')  # Update with the appropriate template name


def Saved_address(request):
   
    return render(request,'product_checkout.html')

def get_saved_addresses(request):
    # Assuming you have a way to identify the logged-in user
    username = request.session.get('username')  # Update this to get the correct user
    user=Custom_users.objects.get(username=username)

    # Fetch the user's saved addresses from the database
    saved_addresses = Users_Address.objects.filter(user=user)
    print(saved_addresses,"...........................................")

    # Convert the queryset to a list of dictionaries
   
    saved_addresses_data = [
        {
            'id': address.id,
            'name': f"{address.first_name} {address.last_name}",
            'address': address.street_address,
            'first_name': address.first_name,
            'last_name': address.last_name,
            'country': address.country,
            'street_address': address.street_address,
            'apartment': address.apartment,
            'city': address.city,
            'state': address.state,
            'zipcode': address.zipcode,
            'phone': address.phone,
            'email': address.email,
        }
        for address in saved_addresses
    ]
        
    

    return JsonResponse({'savedAddresses': saved_addresses_data})



def place_order(request):
    if request.method == 'POST':
        selected_address_details = request.POST.get('saved-address')
        selected_payment_method = request.POST.get('payment-method')
        username = request.session.get('username')
        order_notes = request.POST.get('order_notes', '')
        total_float = request.session.get('total_float')
        print('code enters *****')

        try:
            user = Custom_users.objects.get(username=username)
            address = Users_Address.objects.get(id=selected_address_details)
            print('checks try **********')

            with transaction.atomic():
                # Create a new order instance
                unique_order_number = str(uuid.uuid4())[:8]
                new_order = Order(
                    order_number=unique_order_number,
                    user=user,
                    delivery_address=address,
                    payment_method=selected_payment_method,
                    order_notes=order_notes 
                )
               
                
                if selected_payment_method is None:
                    messages.warning(request, 'Please select a payment method.')
                    return redirect('Product_checkout')

                new_order.save()

                # Clear the existing cartitems associated with the user's order
                new_order.cartitems.clear()

                total_amount_in_paise = int(total_float * 100)  # Convert total_float to paise

                for cart_item in CartItem.objects.filter(user=user):
                    order_item = OrderItem(
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        price=cart_item.product.product_price * cart_item.quantity,
                        orders=new_order,
                    )
                    order_item.save()
                    new_order.cartitems.add(order_item)

                if selected_payment_method == 'OnlinePayment':
                    for order_item in new_order.cartitems.all():
                        product = order_item.product
                        if product.product_stock < order_item.quantity:
                            messages.error(request, 'Out of stock')
                        else:
                            razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                            razorpay_order = razorpay_client.order.create({'amount': total_amount_in_paise, 'currency': 'INR'})

                            return render(request, 'razorpay.html', {'order': new_order, 'razorpay_order': razorpay_order})

                new_order.save()

                for order_item in new_order.cartitems.all():
                    product = order_item.product
                    if product.product_stock >= order_item.quantity:
                        product.product_stock -= order_item.quantity
                        product.save()
                    else:
                        messages.warning(request, f"Insufficient stock for product {product.product_name}")
                        new_order.delete()
                        return redirect('Product_checkout')

                CartItem.objects.filter(user=user).delete()

                return render(request, 'place_order.html', {'order': new_order})
        

        except Custom_users.DoesNotExist:
            print('try exit')
            pass
        except Users_Address.DoesNotExist:
            print('sec try exit')
            return redirect('Product_checkout')

    return redirect('Product_checkout')


def place_order_success(request):
   
    # Get the order_id from the URL parameters
    order_id = request.GET.get('order_id')

    # Fetch the order details using the order_id
    order = Order.objects.get(pk=order_id)  # Assuming your Order model has a primary key 'id'
    username = request.session.get('username')
    user = Custom_users.objects.get(username=username)
    CartItem.objects.filter(user=user).delete()

    # You can add additional logic or data fetching here if needed

    return render(request, 'place_order.html', {'order': order,'username':username})





#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Admin order status  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


def Admin_orderstatus(request):
    orders=Order.objects.all().order_by('-order_date')
    orderitems=OrderItem.objects.all().order_by('-order_date')



   
    # Specify the number of items per page
    items_per_page = 10  # You can adjust this value as needed
    
    # Create a Paginator instance
    paginator = Paginator(orders, items_per_page)
    
    # Get the current page number from the request's GET parameters
    page = request.GET.get('page')
    
    try:
        # Get the corresponding page of orders
        orders = paginator.get_page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver the first page.
        orders = paginator.get_page(1)
    except EmptyPage:
        # If page is out of range, deliver the last page of results.
        orders = paginator.get_page(paginator.num_pages)
    # Create a context dictionary to pass data to the template
    context = {
        'orders': orders,
        'order_items': orderitems,
       
        
    }


    return render(request,'Admin_Orderstatus.html',context)

def update_order_status(request):
    if request.method == 'POST':
        # Loop through form data to update order statuses
        for key, value in request.POST.items():
            if key.startswith('order_') and key.endswith('_status'):
                order_id = key.split('_')[1]
                new_status = value
                try:
                    order = Order.objects.get(id=order_id)
                    order.status = new_status
                    order.save()
                    messages.success(request, f"Order #{order.id} status updated to {new_status}.")
                except Order.DoesNotExist:
                    messages.error(request, f"Order with ID {order_id} not found.")

        return redirect('Admin_orderstatus')  # Redirect to the order status page
    else:
        # Handle GET request or other cases
        return redirect('Admin_orderstatus')  # Redirect to the order status page
    



#>>>>>>>>>>>>>>>>>>>>>>> userside view for account details >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


def view_useraccount_details(request):
    # Default values for unauthenticated users
    total = Decimal(0)
    cart_count = 0

    user_data = None
    user_addresses = None

    # Check if the user is authenticated
    user = request.session.get('username')

    if user:
        user_data = get_object_or_404(Custom_users, username=user)
        total, cart_count = calculate_cart_total(user_data)

    try:
        if user_data:
            # Fetch all associated addresses
            user_addresses = Users_Address.objects.filter(user=user_data)
            

        context = {
            'username': user_data,
            'addresses': user_addresses,
            'cart_total': total,
            'cart_count': cart_count
        }
    except Custom_users.DoesNotExist:
        context = {
            'username': None,
            'addresses': None,
            'cart_total': total,
            'cart_count': cart_count
        }

    return render(request, 'Useraccount_details.html', context)

def delete_address(request, address_id):
    user = request.session.get('username')
    user_data = Custom_users.objects.get(username=user)
       
    # Get the address instance
    address = get_object_or_404(Users_Address, id=address_id)

    # Check if the logged-in user is the owner of the address
    if address.user == user_data:
        address.delete()

    # Redirect back to the user account details page
    return redirect('view_useraccount_details')




    


def order_details(request):
    username = request.session.get('username')  # Assuming the user is logged in
    user = get_object_or_404(Custom_users, username=username)
    orders = Order.objects.filter(user=user).order_by('-id')

    context = {
        'orders': orders,
        'username':username
    }

    return render(request, 'order_details.html', context)

def cancel_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    # Check if the order is cancellable (e.g., it is not already cancelled or delivered)
    if order.status not in ['Cancelled', 'Delivered']:
        # Update the status to 'Cancelled'
        order.status = 'Cancelled'
        
        

        # Save the changes
        order.save()

   
    return JsonResponse({'success':True})

   


def delete_orders(request):
    username = request.session.get('username')  # Assuming the user is logged in
   
    # Get orders with the status "cancelled"
    cancelled_orders = Order.objects.filter(status='Cancelled')

    # Pass the cancelled orders to the template
    context = {'cancelled_orders': cancelled_orders,'username':username}
    

    return render(request, "Delete_orders.html",context)


def edit_address(request, address_id):
    # Assuming you have the address_id from the request or other means
    address = get_object_or_404(Users_Address, id=address_id)

    if request.method == 'POST':
        # Update the address fields based on the form data
        address.first_name = request.POST.get('first_name', address.first_name)
        address.last_name = request.POST.get('last_name', address.last_name)
        address.country = request.POST.get('country', address.country)
        address.street_address = request.POST.get('street_address', address.street_address)
        address.apartment = request.POST.get('apartment', address.apartment)
        address.city = request.POST.get('city', address.city)
        address.state = request.POST.get('state', address.state)
        address.zipcode = request.POST.get('zipcode', address.zipcode)
        address.phone = request.POST.get('phone', address.phone)
        address.email = request.POST.get('email', address.email)

        # Save the changes
        address.save()

        # Redirect to a page or render a template
        return redirect('view_useraccount_details')  # Replace with your desired URL

    # Render the form with the existing address data
    context = {
        'address': address,
    }
    return render(request, 'edit_address.html', context)



# >>>>>>>>>>>>>>>>>>>>>>>>>>>>> product offer displaying / adding / deleting >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


def Admin_productoffer(request):

    productoffers={
        'productoffer':Product_Offer.objects.all()
    }

    return render(request,'Admin_productoffer.html',productoffers)

def productoffer_add(request):
    products = {
        'product': Product_Details.objects.all()
    }
    
    if request.method == 'POST':
        product_id = request.POST.get('product')
        offer_type = request.POST.get('offer_type')
        discount_value = request.POST.get('discount_value')
        expiration_date = request.POST.get('expiration_date')

        if product_id == "" or offer_type == "" or discount_value == "" or expiration_date == "":
            messages.error(request, "Empty form can't be submitted")
            return redirect('productoffer_add')

        # Perform necessary validation on input data before saving
        else:
            product = Product_Details.objects.get(product_id=product_id)

            # Convert the discount_value to an integer
            discount_value = int(discount_value)

            if offer_type == 'percentage':
                # Check if the percentage discount is less than 30%
                if discount_value > 30 or discount_value < 0:
                    messages.error(request, "Percentage discount must be lessthan 30% or greaterthan 0")
                    return redirect(productoffer_add)
                else:
                    Product_Offer.objects.create(
                        product=product,
                        offer_type=offer_type,
                        discount_value=discount_value,
                        expiration_date=expiration_date
                    )
            elif offer_type == 'fixed':
                # Check if the fixed discount is less than 150
                if discount_value > 150 or discount_value < 0 :
                    messages.error(request, "Fixed discount must be lessthan RS.150 or greaterthan 0")
                    return redirect(productoffer_add)
                else:
                    Product_Offer.objects.create(
                        product=product,
                        offer_type=offer_type,
                        discount_value=discount_value,
                        expiration_date=expiration_date
                    )
            else:
                messages.error(request, "Invalid offer type")

        return redirect('Admin_productoffer')

    return render(request, 'Adminproductoffer_add.html', products)


def productoffer_delete(request,productoffer_id):
    productoffer=get_object_or_404(Product_Offer,id=productoffer_id)
    if request.method=='POST':
        productoffer.is_active = not productoffer.is_active
        productoffer.save()
        return redirect(Admin_productoffer)
    return HttpResponseRedirect(reverse(Admin_productoffer))
    
        
    








#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> category offer displaying / adding / deleting >>>>>>>>>>>>>>>>>>>>>>

def Admin_categoryoffer(request):

    categoryoffers={
        'categoryoffer':Category_Offer.objects.all()
    }

    return render(request,'Admin_categoryoffer.html',categoryoffers)

def Categoryoffer_add(request):
    productcategory = {
        'product_categories': Product_Category.objects.all()
    }

    if request.method == 'POST':
        category_id = request.POST.get('category')
        offer_type = request.POST.get('offer_type')
        discount_value = request.POST.get('discount_value')
        expiration_date = request.POST.get('expiration_date')

        if category_id == "" or offer_type == "" or discount_value == "" or expiration_date == "":
            messages.error(request, "Empty form can't be submitted")
            return redirect('Categoryoffer_add')

        # Perform necessary validation on input data before saving
        else:
            category = Product_Category.objects.get(category_id=category_id)

            # Convert the discount_value to an integer
            discount_value = int(discount_value)

            if offer_type == 'percentage':
                # Check if the percentage discount is less than 30%
                if discount_value > 30 or discount_value < 0:
                    messages.error(request, "Percentage discount must be less than 30% or greater than 0")
                    return redirect('Categoryoffer_add')
                else:
                    Category_Offer.objects.create(
                        category=category,
                        offer_type=offer_type,
                        discount_value=discount_value,
                        expiration_date=expiration_date
                    )
            elif offer_type == 'fixed':
                # Check if the fixed discount is less than 150
                if discount_value > 150 or discount_value < 0:
                    messages.error(request, "Fixed discount must be less than RS.150 or greater than 0")
                    return redirect('Categoryoffer_add')
                else:
                    Category_Offer.objects.create(
                        category=category,
                        offer_type=offer_type,
                        discount_value=discount_value,
                        expiration_date=expiration_date
                    )
            else:
                messages.error(request, "Invalid offer type")

        return redirect('Admin_categoryoffer')
    
    return render(request, 'Categoryoffer_add.html', productcategory)



def categoryoffer_disable(request, category_offer_id):
    categoryoffer = get_object_or_404(Category_Offer, id=category_offer_id)

    if request.method == 'POST':
        # Toggle the is_active field
        categoryoffer.is_active = not categoryoffer.is_active
        categoryoffer.save()

    return HttpResponseRedirect(reverse('Admin_categoryoffer'))



#<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> download order invoce using reportlab >>>>>>>>>>>>>>>>>>>>>>>>>



from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.template import Context

from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Order, OrderItem

def generate_pdf(request,order_id):
    # Retrieve the order or return a 404 response if it doesn't exist
    order = get_object_or_404(Order, id=order_id)
    print(order_id,'////////////////////////')
    total= request.session.get('total_float')

    # Retrieve order items for the given order
    order_items = OrderItem.objects.filter(order=order)

    # Render the PDF content
    pdf_content = render_to_pdf('invoice_template.html', {'order': order, 'order_items': order_items,'total':total})

    if pdf_content:
        # Create an HttpResponse with the PDF content
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="order_invoice_{order_id}.pdf"'
        return response

    return HttpResponse("Error generating PDF.", status=500)

def render_to_pdf(template_path, context):
    template = get_template(template_path)
    html = template.render(context)
    result = BytesIO()

    # Generate the PDF using pisa.pisaDocument
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        return result.getvalue()
    else:
        # You may want to log or handle the error here
        print("PDF generation error:", pdf.err)
        return None



  
#>>>>>>>>>>>>>>>>>. admin sales report >>>>>>>>>>>>>>>>>>>>>>>>

from django.db.models import Sum
from django.http import HttpResponse
from django.template.loader import render_to_string
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib.pagesizes import letter
import datetime
import pytz
from django.utils import timezone

import matplotlib.pyplot as plt
from io import BytesIO
from django.http import HttpResponse
from matplotlib.backends.backend_agg import FigureCanvasAgg
from datetime import datetime


def generate_sales_chart(sales_data):
    # Extract date and sales data for the chart
    dates = [entry['order_date'].date() for entry in sales_data]
    total_sales = [entry['total_sales'] for entry in sales_data]

    # Create a figure and plot the data
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(dates, total_sales, marker='o', linestyle='-')

    # Customize the chart appearance
    ax.set(xlabel='Date', ylabel='Total Sales',
           title='Sales Over Time')
    ax.grid()
    plt.xticks(rotation=45)  # Rotate x-axis labels for readability

    # Create a buffer to save the chart image
    buffer = BytesIO()
    canvas = FigureCanvasAgg(fig)
    canvas.print_png(buffer)

    return buffer

def download_sales_chart(request):
    # Query sales data
    sales_data = OrderItem.objects.values('order_date').annotate(total_sales=Sum('quantity'))

    # Generate sales chart
    chart_buffer = generate_sales_chart(sales_data)

    # Create the HttpResponse object with the appropriate image headers
    response = HttpResponse(chart_buffer.getvalue(), content_type='image/png')
    response['Content-Disposition'] = 'attachment; filename="sales_chart.png"'

    return response



from django.db.models import Sum
from django.utils import timezone
from datetime import date, timedelta

def sales_report(request):
  
    start_date = request.GET.get('start_date', (date.today() - timedelta(days=15)).isoformat())
    end_date = request.GET.get('end_date', date.today().isoformat())

    # Print for debugging purposes
    print("Start Date:", start_date)
    print("End Date:", end_date)

    # Get the sales data without filtering
    sales_data = OrderItem.objects.values('product__product_name')

    if start_date and end_date:
        # Convert start_date and end_date to datetime objects
        start_datetime = timezone.make_aware(timezone.datetime.strptime(start_date, '%Y-%m-%d'))
        end_datetime = timezone.make_aware(timezone.datetime.strptime(end_date, '%Y-%m-%d'))
        
        # Filter sales data based on the date range
        sales_data = sales_data.filter(order__order_date__range=(start_datetime, end_datetime))

    # Annotate the total sales
    sales_data = sales_data.annotate(total_sales=Sum('quantity'))

    return render(request, 'Adminsales_report.html', {'sales_data': sales_data})




def generate_sales_report_pdf(sales_data):
    buffer = BytesIO()

    # Create the PDF object using BytesIO as its "file"
    p = canvas.Canvas(buffer, pagesize=letter)

    # Set PDF title
    p.setTitle("Sales Report")

    # Set styles
    p.setFont("Helvetica", 12)

    # Define the table headers
    table_data = [['Product Name', 'Total Sales Quantity']]

    # Draw table headers
    x, y = 40, 750
    for col_num, cell_value in enumerate(table_data[0]):
        p.drawString(x, y, cell_value)
        x += 200

    # Draw table rows
    y -= 20
    for entry in sales_data:
        row = [entry['product__product_name'], entry['total_sales']]
        x = 40
        for col_num, cell_value in enumerate(row):
            p.drawString(x, y, str(cell_value))
            x += 200
        y -= 20

    # Close the PDF object cleanly
    p.showPage()
    p.save()

    # Reset the buffer for reading
    buffer.seek(0)
    return buffer

def download_sales_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Print for debugging purposes
    print("Start Date:", start_date)
    print("End Date:", end_date)

    # Get the sales data without filtering
    # sales_data = OrderItem.objects.values('product__product_name')

    if start_date and end_date:
        start_datetime = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_datetime = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()

        # Filter sales data based on the date range
        # sales_data = sales_data.filter(order__order_date__range=(start_datetime, end_datetime))
        sales_data = OrderItem.objects.values('product__product_name').filter(
            order__order_date__range=(start_datetime, end_datetime)
        ).annotate(total_sales=Sum('quantity'))

    # # Annotate the total sales
    # sales_data = sales_data.annotate(total_sales=Sum('quantity'))
    else:
        # If no date range is specified, retrieve all sales data
        sales_data = OrderItem.objects.values('product__product_name').annotate(total_sales=Sum('quantity'))


    # Generate the PDF content
    pdf_buffer = generate_sales_report_pdf(sales_data)

    # Create the HttpResponse object with the appropriate PDF headers
    response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

    return response








#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> paginator giving in products >>>>>>>>>>>>>>>>>>>>>>>>>>>>




from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

def shopitems(request):

    total = Decimal(0)
    cart_count = 0

    username = request.session.get('username')

    if username:
        user = get_object_or_404(Custom_users, username=username)
        total, cart_count = calculate_cart_total(user)

 
    # Assuming you already have a queryset of products named 'product_list'
    all_products = Product_Details.objects.all().order_by('product_name')

    # Number of products to be displayed per page
    items_per_page = 12  
    # Create a Paginator instance
    paginator = Paginator(all_products, items_per_page)

    page = request.GET.get('page')  # Get the current page number from the request
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # If the page is not an integer, set to the first page
        products = paginator.page(1)
    except EmptyPage:
        # If the page is out of range (e.g., 9999), deliver the last page
        products = paginator.page(paginator.num_pages)
    context = {
        
        'cart_total': total,
        'cart_count': cart_count,
        'products': products
    }


    return render(request, 'products.html', context)




#>>>>>>>>>>>>>>>>>>>>>>>>>>>> dashboard setting on the basis of sales >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.


from django.utils import timezone
from django.db.models import Sum
from django.shortcuts import render
from datetime import datetime
from .models import Order, OrderItem, Product_Details

def dashboard(request):
    
    if request.method == "POST":
        start_date= request.POST.get("startdate")
        end_date = request.POST.get("enddate")
        
        

        # Convert start_date_str and end_date_str to datetime objects
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
  
    else:
        # Calculate the default date range as the past 15 days from the current date
        end_date = timezone.now()  # Current date and time
        if not timezone.is_aware(end_date):
            end_date = timezone.make_aware(end_date)
        
        start_date = end_date - timedelta(days=7)  # Calculate the start date as 15 days ago
        if not timezone.is_aware(start_date):
            start_date = timezone.make_aware(start_date)
        print(start_date)
        print(end_date)

    # Filter orders and items for the specified date range
    orders = Order.objects.filter(order_date__range=(start_date, end_date))
    items = OrderItem.objects.filter(orders__in=orders, product__isnull=False)

    # Create a dictionary to store sales data
    sales_data = {}

    for item in items:
        product_name = item.product.product_name

        if product_name in sales_data:
            sales_data[product_name] += item.quantity
        else:
            sales_data[product_name] = item.quantity

    # Sort the sales_data dictionary by product name to make it easier to display in the template
    sorted_sales_data = dict(sorted(sales_data.items()))

    # Calculate the total sales
    total_sales = sum(sorted_sales_data.values())

    # Get the top-selling product
    top_product = max(sorted_sales_data, key=sorted_sales_data.get, default=None)

    context = {
        "sales_data": sorted_sales_data,
        "total_sales": total_sales,
        "top_product": top_product,
        "start_date": start_date.date(),
        "end_date": end_date.date(),
    }

    return render(request, "dashboard.html", context)



def contact_us(request):
    username=request.session.get('username')
    if request.method == 'POST':
        name=request.POST.get('name')
        email=request.POST.get('email')
        text=request.POST.get('text')

        if name != username:
            messages.error(request, 'You can only post messages with your username.')

        elif name == "" or email == "" or text == "":
            messages.error(request,'empty form canot be submit')
            return redirect(contact)
        else:
            msg=Contact_with_us(name=name,email=email,text=text)
            msg.save()
            messages.success(request,'your message successfully send')


    return render(request,'contact.html')

def admin_usersmsg(request):
    msg=Contact_with_us.objects.all()
    context={
        'msgs':msg
    }

    return render(request,'Users_messages.html',context)