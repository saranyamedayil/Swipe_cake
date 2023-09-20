from django.shortcuts import render,redirect
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, HttpResponseRedirect, reverse
from .models import *
from .helpers import send_otp_phone
from django.http import JsonResponse
import random
from django.views.generic import ListView
from decimal import Decimal
from django.db.models import Q



# Create your views here.
def Users_homebefore(request):
    message = 'please login your account'
    return render(request, 'home_before.html', {'msg': message})



@never_cache 
def Users_login(request):
    if "username"in request.session:
        return redirect(Users_homeafter)
    
    if request.method=='POST':

        username=request.POST.get('username')
        password=request.POST.get('password')

        try:
            user = Custom_users.objects.get(username=username)
        except ObjectDoesNotExist:
            messages.error(request, "You are not authorized to log in.")
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
                messages.error(request, "Passwords don't match")
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
                    otp = random.randint(100000, 999999)
                    otp_to_ph = str(otp)
                    print(".............................", otp_to_ph)
                    user.password = password
                    user.save()

                    # Save user information in the session
                    request.session['phonenumber'] = phonenumber
                    request.session['otp'] = otp_to_ph
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
                
                user_obj.save()
                request.session['username'] = user_obj.username
                return redirect('login')  # Redirect to the login page upon successful OTP verification
            else:
                messages.error(request, 'Invalid OTP')
                user_obj.delete()
                return render(request, 'Usersignin.html')

        except Custom_users.DoesNotExist:
            messages.error(request, 'Invalid phone number')

    return render(request, 'Usersignin.html')




# @never_cache
# def Users_homeafter(request):
    
#     product = Product_Details.objects.all()
    
#     context = {'product': product}
    
#     if 'username' in request.session:
#             username = request.session.get('username')

#         if username:
#             # Get the user object associated with the username
#             user = Custom_users.objects.get(username=username)

#             cart_items = CartItem.objects.filter(user=user)

#             subtotal_dict = {}
#             total =Decimal(0)
#             for item in cart_items:
#             # Calculate the total price for each cart item
#                 item_total = item.quantity * item.product.product_price
#                 if item.product.product_category.category_name in subtotal_dict:
#                     # If it exists, add the item total to the existing subtotal
#                     subtotal_dict[item.product.product_category.category_name] += item_total
#                 else:
#                     # If it doesn't exist, create a new entry
#                     subtotal_dict[item.product.product_category.category_name] = item_total

#                 # Add item total to the total
#                 total += item_total
        
#             return render(request,"home_after.html",context,{'cart_total': total})  #rechecking the login user is in the session or not then it allows to access home page
#     return redirect(Users_login)
@never_cache
def Users_homeafter(request):
    context = {}

    product = Product_Details.objects.all()
    context['product'] = product

     # Retrieve all categories
    categories = Product_Category.objects.all()
    context['categories'] = categories  # Add 'categories' to the context

    if 'username' in request.session:
        username = request.session.get('username')

        if username:
            # Get the user object associated with the username
            user = Custom_users.objects.get(username=username)

            cart_items = CartItem.objects.filter(user=user)

            subtotal_dict = {}
            total = Decimal(0)

            for item in cart_items:
                # Calculate the total price for each cart item
                item_total = item.quantity * item.product.product_price
                if item.product.product_category.category_name in subtotal_dict:
                    # If it exists, add the item total to the existing subtotal
                    subtotal_dict[item.product.product_category.category_name] += item_total
                else:
                    # If it doesn't exist, create a new entry
                    subtotal_dict[item.product.product_category.category_name] = item_total

                # Add item total to the total
                total += item_total

            # Add 'cart_total' to the context
            context['cart_total'] = total

            return render(request, "home_after.html", context)  # Pass the context with 'cart_total'
    
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




#>>>>>>>>>>>>>>>>>>>>>>>>> user details >>>>>>>>>>>>>>>>>>>>>>>>>>>

def Users_details(request):
    user={
        'users':Custom_users.objects.all()
    }
    return render(request,'Users_details.html',user)


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
        return JsonResponse({'success': True, 'new_value': not current_value})
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


    

    

#??????????????????????????????????????  products details based codes ??????????????????????????????????



def Product_Details_all(request):
    products ={
        'product':Product_Details.objects.all()
    }
    

    return render(request,'Product_details.html',products)


def Product_add(request):
    categories = Product_Category.objects.all()

    if request.method=='POST':
        try:
            productname=request.POST['productname']
            category_id=request.POST['category']
            stock=request.POST['stock']
            price=request.POST['price']
            image=request.FILES['image']
            quantity = request.POST.get('quantity', 0)  # Default to 0 if not provided

            # Check if the specified category exists
            try:
                category = Product_Category.objects.get(pk=category_id)

            except Product_Category.DoesNotExist:
                    # Handle the case where the category doesn't exist (you can create it if needed)
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
            messages.error(request, f'Error adding product: {str(e)}')
            return redirect(Product_Details_all)
    
    
    return render(request,'Product_Add.html',{'categories': categories})



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
    template_name = 'product_categorywise.html'  # Replace with your desired template name
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

        # Calculate cart total using the calculate_cart_total function
        if 'username' in self.request.session:
            username = self.request.session.get('username')

            if username:
                user = Custom_users.objects.get(username=username)
                total = calculate_cart_total(user)
                context['cart_total'] = total  # Add 'cart_total' to the context

        context['category_name'] = category_name
        return context




#>>>>>>>>>>>>>>>>>>>>>>>>>>> add to cart $ displaying & deleting >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


def add_to_cart(request, product_id):
    product = get_object_or_404(Product_Details, product_id=product_id)
    
    # Retrieve the username from the session
    username = request.session.get('username')
    
    # Get the user object associated with the username
    user = Custom_users.objects.get(username=username)
    
    # Check if the user already has this product in their cart
    existing_cart_item = CartItem.objects.filter(user=user, product=product).first()
    
    if existing_cart_item:
        # Update the quantity of the existing cart item
        existing_cart_item.quantity += 1
        existing_cart_item.save()
    else:
        # Create a new cart item for the user
        new_cart_item = CartItem(user=user, product=product, quantity=1)
        new_cart_item.save()
        messages.success(request, 'Product added to your cart')

            # Remove the product from the wishlist
        WishlistItem.objects.filter(user=user, product=product).delete()

    
    return redirect(Users_homeafter)  # Redirect to product list page




def view_cart(request):
    # Retrieve the username from the session
    username = request.session.get('username')

    if username:
        # Get the user object associated with the username
        user = Custom_users.objects.get(username=username)

        cart_items = CartItem.objects.filter(user=user)

        subtotal_dict = {}
        total =Decimal(0)
        for item in cart_items:
        # Calculate the total price for each cart item
            item_total = item.quantity * item.product.product_price
            if item.product.product_category.category_name in subtotal_dict:
                # If it exists, add the item total to the existing subtotal
                subtotal_dict[item.product.product_category.category_name] += item_total
            else:
                # If it doesn't exist, create a new entry
                subtotal_dict[item.product.product_category.category_name] = item_total

            # Add item total to the total
            total += item_total

        return render(request, 'shoping-cart.html', {'cart_items': cart_items, 'subtotal_dict': subtotal_dict, 'cart_total': total})
    else:
        # User is not logged in, so provide a login form
        messages.warning(request, 'Please log in to view your cart.')
        return redirect('login')  # Redirect to your login page name


def delete_from_cart(request, item_id):
    username = request.session.get('username')
    if username:
        # Get the user object associated with the username
        user = Custom_users.objects.get(username=username)

        
    # Get the cart item to delete
        cart_item = get_object_or_404(CartItem, id=item_id, user=user)

    # Delete the cart item
        cart_item.delete()

    # Redirect back to the cart page or any other desired page
    return redirect(view_cart)





#............................................ calculating the cart total into seperate function ...................................

def calculate_cart_total(user):
    cart_items = CartItem.objects.filter(user=user)
    total = Decimal(0)

    for item in cart_items:
        # Calculate the total price for each cart item
        item_total = item.quantity * item.product.product_price
        total += item_total

    return total


#???????????????????????????????????? about page ????????????????????????

def about(request):
    username = request.session.get('username')
    total = Decimal(0)  # Default total for unauthenticated users

    if username:
        # Get the user object associated with the username
        user = Custom_users.objects.get(username=username)
        total = calculate_cart_total(user)

    return render(request, 'about.html', {'cart_total': total})



########################### contact page ??????????????????????????????

def contact(request):
    username = request.session.get('username')
    total = Decimal(0)  # Default total for unauthenticated users

    if username:
        # Get the user object associated with the username
        user = Custom_users.objects.get(username=username)
        total = calculate_cart_total(user)

    return render(request,'contact.html',{'cart_total': total})




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

   

    if username:
        user=Custom_users.objects.get(username=username)
        total = calculate_cart_total(user)

        wishlist_items=WishlistItem.objects.filter(user=user)

    else:
        messages.warning(request, 'please login your account')
        return redirect(Users_login)
    

    return render(request,'User_wishlist.html',{'wishlist':wishlist_items,'cart_total': total})


def delete_from_wishlist(request, item_id):
    username = request.session.get('username')
    if username:
        # Get the user object associated with the username
        user = Custom_users.objects.get(username=username)

        
    # Get the cart item to delete
        wishlist_item = get_object_or_404(WishlistItem, id=item_id, user=user)

    # Delete the cart item
        wishlist_item.delete()

    # Redirect back to the wishlist page 
    return redirect(View_userswishlist)



















