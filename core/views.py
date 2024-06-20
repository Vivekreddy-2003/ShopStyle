from django.conf import settings
from django.db.models import Q
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView,DetailView,View
from . models import Item,OrderItem,Order,Address,Payment,Coupon,Refund,UserProfile
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from .forms import CheckoutForm,CouponForm,RefundForm
from .models import SIZE_LABELS
from django.utils.datastructures import MultiValueDictKeyError  # Import MultiValueDictKeyError
from django_countries import countries
from django.core.paginator import Paginator
## for email verify by admin ##
from allauth.account.views import SignupView
from django.contrib import messages
###############################
import random
import string
# Create your views here.

import stripe
stripe.api_key=settings.STRIPE_SECRET_KEY
GENDER_LABELS=(
    ('men','men'),
    ('boys','boys')
)
CATEGORY_CHOICES=(
    ('shirt','shirt'),
    ('shorts','shorts'),
    ('outwear','outwear'),
    ('shoes','shoes')
)
SIZE_LABELS=(
    ('S','28'),
    ('M','30'),
    ('L','40'),
    ('XL','42'),
    ('XXL','44')
)
def carousel_filter(request):
    if request.method == 'POST':
        gender_states = request.POST.get('gender_state')
        categories = request.POST.getlist('category[]')
        sizes = request.POST.getlist('size[]')
        price = request.POST.get('price')

        """ # Start with an empty queryset
        if gender_states:
            filter_items = Item.objects.filter(gender=gender_states)
        else:
            filter_items=Item.objects.all()
        print(filter_items)
        # Filter items based on selected sizes
        combined_queryset = Item.objects.none()
        if categories:
                for category in categories:
                    size_queryset = Item.objects.filter(catgeory=category)
                    combined_queryset |= size_queryset
            # Apply filters for sizes
        filter_items = filter_items.filter(category__in=categories)
        print('filter-category',filter_items)
        combined_queryset = Item.objects.none()

        if sizes:
            print('enterd if block')
            for size in sizes:
                size_queryset = Item.objects.filter(size=size)
                combined_queryset |= size_queryset
        # Filter items based on selected categories
        if categories:
            category_queryset = Item.objects.filter(category__in=categories)
            combined_queryset = combined_queryset & category_queryset

        # Filter items based on gender
        
        # Order items based on price
        if price == 'LowtoHigh':
            filter_items = filter_items.order_by('price')
        elif price == 'HightoLow':
            filter_items = filter_items.order_by('-price')

        # Render the response with filtered items
        return render(request, 'carousel_item.html', {'items': filter_items})"""
        # Start with an empty queryset
        combined_queryset = Item.objects.all()

        # Filter items based on gender
        if gender_states:
            print('gender',gender_states)
            filter_items = combined_queryset.filter(gender=gender_states)
            print('if-filter-gender',filter_items)
        else:
            filter_items = combined_queryset
            print('else-filter-gender',filter_items)
        # Filter items based on selected categories
        if categories:
            print('categories',categories)
            category_queryset = Item.objects.filter(category__in=categories)
            filter_items = filter_items.filter(category__in=categories)
            print('if-filter-categories',filter_items)

        # Filter items based on selected sizes
        if sizes:
            print('sizes',sizes)
            size_queryset = Item.objects.filter(size__in=sizes)
            filter_items = filter_items.filter(size__in=sizes)
            print('if-filter-sizes',filter_items)
        # Order items based on price
        if price == 'LowtoHigh':
            filter_items = filter_items.order_by('price')
        elif price == 'HightoLow':
            filter_items = filter_items.order_by('-price')
        print('filter-all',filter_items)
        # Render the response with filtered items
        return render(request, 'detailCategory.html', {'items': filter_items})
class HomeView(ListView):
    model=Item
    paginate_by=4
    template_name = "home.html"

class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the category of the current item
        category = self.object.category
        # Get the list of items with the same category, excluding the current item
        related_items = Item.objects.filter(category=category).exclude(pk=self.object.pk)
        print(related_items)
        # Add the related items to the context
        context['related_items'] = related_items
        return context
    
    def get_size_label(self):
        size = self.object.size
        print('size')
        for label, value in self.SIZE_LABELS:
            if value == size:
                return label
        return None

def detail_puma(request):
    try:   
        allItems=Item.objects.filter(label='PU')
        if not allItems.exists():
            messages.warning(request, "No items found in the selected category")
            return redirect("core:home")
        return render(request,'puma.html',{
            'items':allItems,
            })
    except Exception as e:
            # send an email to our selves
            messages.warning(request,"Click properly on Item.")
            print('puma-error',e)
            return redirect('/')
    
def carousel_item(request):
    try:
        all_items = Item.objects.all()
        paginator = Paginator(all_items, 9)  # Paginate by 4 items per page

        page_number = request.GET.get('page')
        items = paginator.get_page(page_number)

        return render(request, 'carousel_item.html', {
            'items': items,
            'paginator': paginator,
            'page_obj': items,
            'is_paginated': True,
        })
    except Exception as e:
            # send an email to our selves
            messages.warning(request,"Click properly on Carousel.")
            print('carousel-error',e)
            return redirect('/')
    
class DeleteAddressView(View):
    def post(self, request):
        user=request.user;
        address_id = request.POST.get('address_id')
        try:
            address = Address.objects.get(pk=address_id)
            address.delete()
            # Redirect to a success URL or render a success message
            address = Address.objects.filter(user=user)
            orders=Order.objects.filter(user=user,ordered=True)
            messages.warning(request,"Address deleted.")
            return render(request,'profile.html',{
                'items': orders,
                'address':address,

            })
        except Address.DoesNotExist:
            messages.warning(request,"Address can't be deleted.")
            return redirect('core:profile')
    def get(self,request):
        return redirect('core:profile')
    
def profile(request):
    try:
        user=request.user;
        orders=Order.objects.filter(user=user,ordered=True)
        address = Address.objects.filter(user=user)
        print(orders)
        print(address)
        for add in address:
            country_name = dict(countries)[add.country.code]
            print(country_name)

        for order in orders:
            print('paid',order.payment.amount)
            print('total',order.whole_total())
            if order.payment.amount != order.whole_total():
                print('coupon')
                coupon_amount = order.whole_total() - order.payment.amount
                print(coupon_amount)
                order.coupon_amount = coupon_amount
            else:
                order.coupon_amount = 0.0
        return render(request,'profile.html',{
            'items': orders,
            'address':address
        })
    except Exception as e:
        print(e)
        messages.warning(request,"Can't go back by backpress.")
        return redirect('core:home')



def apply_filters(request):
    category_value = request.POST.get('category')
    if request.method == 'POST':
        try:
            print(request.POST)
            # Get the values of the checked checkboxes
            gender_states = request.POST['gender_state']
            categories = request.POST.getlist('category[]')
            category_value = request.POST.get('category')
            #category_value=request.POST['category_value']
            sizes = request.POST.getlist('size[]')
            # Get the value of the selected radio button (for price)
            price = request.POST.get('price')
            # Filter the items based on gender
            """allItems=Item.objects.all()
            filterItems= Item.objects.filter(gender=gender_states)
            print("filter-items-gender:" , filterItems)"""
            # Apply filters for categories
            """if categories:
                for category in categories:
                    filterItems = filterItems.filter(category=category)
                print('filter-Items-category',filterItems)"""
            # Apply filters for sizes
            combined_queryset = Item.objects.none()

            if sizes:
                print('enterd if block')
                for size in sizes:
                    size_queryset = Item.objects.filter(size=size)
                    combined_queryset |= size_queryset
            else:
                print('entered else block')
                # Retrieve size options
                size_options = ['S','M','L','XL','XXl']
                print('sizes', size_options)
                # Now size_options contains all the size values
                for size in size_options:
                    print(size)
                    size_queryset = Item.objects.filter(size=size)
                    print(f"Size {size} items:", size_queryset)
                    combined_queryset |= size_queryset
                    print(combined_queryset)

            # Now, combined_queryset contains all items for all sizes
            print("Combined queryset for selected sizes:", combined_queryset)


            filterItems=combined_queryset.filter(gender=gender_states)
            print('filter-gender',gender_states)
            filterItems=filterItems.filter(category=category_value)
            print('filter-category',filterItems)
            if price == 'LowtoHigh':
                filterItems = filterItems.order_by('price')
            elif price == 'HightoLow':
                filterItems = filterItems.order_by('-price')

            print("Final-filter-Items",filterItems)
            # Process the checked values as needed
            #print(category_value)
            print("Gender States:", gender_states)
            print("Categories:", categories)
            print("Sizes:", sizes)
            print("Price:", price)
            
            # Render the response or redirect to another page
            # return render(request, 'result.html', {'checked_values': gender_states})
            # or
            # return redirect('some_url_name')
            return render(request,'detailCategory.html',{
                'items': filterItems
            })
        except MultiValueDictKeyError:
            # Handle the case when 'gender_state' is not found in POST data
            messages.warning(request, "Select Gender Category")
            filterItems = Item.objects.filter(category=category_value)
            return render(request,'detailCategory.html',{
                'items': filterItems
            })
        except ValueError as e:
            # Handle the case when 'gender_state' is empty
            error_message = str(e)  # Get the error message from the exception
            messages.warning(request, "Select Gender Category")
            filterItems = Item.objects.filter(category=category_value)
            return render(request,'detailCategory.html',{
                'items': filterItems
            })
    else:
        # Handle GET request if needed
        messages.info(request, "select category")
        return redirect('core:detail')
        
def detail_Category(request):
    try:
        if request.method == 'POST':
            # Get the lowercase category abbreviation from the form data
            category_abbreviation = request.POST['category'].lower()
            print(category_abbreviation)
            # Filter items based on the lowercase category abbreviation
            allItems = Item.objects.filter(category=category_abbreviation)
            print(allItems)
            # If no items are found, handle the error appropriately
            if not allItems.exists():
                messages.warning(request, "No items found in the selected category")
                return redirect("core:home")
            
            # Render the template with the filtered items
            return render(request,'detailCategory.html',{
                'items': allItems
            })
        else:
            # Handle GET requests appropriately (if needed)
            messages.warning(request, "Enter items from the categories")
            return redirect("core:home")
    except Exception as e:
        return redirect('core:home') 

def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits,k=20))

def product_Page(request):
    return render(request,'product.html')



class OrderSummaryView(LoginRequiredMixin,View):
    def get(self,*args,**kwargs):
        try:
            order=Order.objects.get(user=self.request.user,ordered=False)
            context={
                'object':order
                    }
            return render(self.request,'order_summary.html',context)
        except ObjectDoesNotExist:
            messages.warning(self.request,"You do not have an active order")
            return redirect('/')

class PaymentView(View):
    def get(self, *args, **kwargs):
        try:
            order=Order.objects.get(user=self.request.user,ordered=False)
            if order.billing_address:
                context = {
                    'order': order,
                    'DISPLAY_COUPON_FORM': False,
                }
                return render(self.request, "item_list.html", context)
            else:
                messages.warning(
                    self.request, "You have not added a billing address")
                return redirect("core:checkout")
        except Exception as e:
            return redirect('core:home')
    def post(self,*args,**kwargs):
        #print('request recieved')
        #print('now it is received twice')
        try:
            order=Order.objects.get(user=self.request.user,ordered=False)
            token=self.request.POST.get('stripeToken')
            #print('token received',token)
            amount=int(order.get_total() * 100)#get total amounts to convert to cents(*100)
            try:
                #creating stripe charge
                source = stripe.Source.create(
                    type="card",
                    token=token
                    )   
                charge=stripe.PaymentIntent.create( 
                    amount=amount,
                    currency='inr',
                    source=source.id
                    ) 
                    #create the payment
                #print('created charge')
                payment=Payment(stripe_charge_id=charge['id'],user=self.request.user,amount=order.get_total())
                print('payment',payment)
                payment.save()
                #update ordered items of quantity =1
                order_items=order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()
                #print('paymentsaved')
                #assign payment to Order
                order.ordered=True # make order
                order.payment=payment #add paument to order
                #add reference code
                order.ref_code=create_ref_code()
                order.save() #Order saving
                messages.warning(self.request,"Your order was successful1")
                return redirect('core:profile')
            
            except stripe.error.CardError as e:
                body=e.json_body
                err=body.get('error',{})
                messages.warning(self.request,f"{err.get('message')}")
                return redirect('/')
            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                messages.warning(self.request,"rate limit error")
                print('err2')
                return redirect('/')
            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                messages.warning(self.request,"Invalid parameters")
                print('err3',e)
                return redirect('/')
            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                messages.warning(self.request,"Not autheticated")
                print('err4')
                return redirect('/')
            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                messages.warning(self.request,"Network error")
                print('err5')
                return redirect('/')
            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                messages.warning(self.request,"Something went wrong. You were not charged.Please try again")
                print('err6')
                return redirect('/')
            except Exception as e:
                # send an email to our selves
                messages.warning(self.request,"A serious error ocuured . we have been notified.")
                print('err7')
                return redirect('/')
        except Exception as e:
            return redirect('core:checkout')


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid

class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                value = shipping_address_qs[0].street_address
                print(value)
                context.update(
                    {'default_shipping_address': value, })
                
            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
            )
            if billing_address_qs.exists():
                value = billing_address_qs[0].street_address
                print(value)
                context.update(
                    {
                        'default_billing_address':value,
                        }
                    )
            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("core:checkout")
    def post(self,*args,**kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print("Using the default shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new shipping address")
                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_country = form.cleaned_data.get(
                        'shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form([shipping_address1, shipping_country, shipping_zip]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            zip=shipping_zip,
                            address_type='S'
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")

                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()

                elif use_default_billing:
                    print("Using the defualt billing address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default billing address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new billing address")
                    billing_address1 = form.cleaned_data.get(
                        'billing_address')
                    billing_address2 = form.cleaned_data.get(
                        'billing_address2')
                    billing_country = form.cleaned_data.get(
                        'billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')

                    if is_valid_form([billing_address1, billing_country, billing_zip]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            zip=billing_zip,
                            address_type='B'
                        )
                        billing_address.save()

                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get(
                            'set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required billing address fields")

                payment_option = form.cleaned_data.get('payment_option')

                if payment_option == 'S':
                    return redirect('core:payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('core:payment', payment_option='paypal')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:order-summary")
        
@login_required
def add_to_cart(request,slug):
    item=get_object_or_404(Item,slug=slug)#take the item of product
    order_item ,created= OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
        )#create item as OrderItem
    order_qs=Order.objects.filter(user=request.user,ordered=False)#Take the order which is not placed or completed (ordered=False) of user
    if order_qs.exists():# if order exists
        order=order_qs[0] #selects first one 
        # check if order item is in the order
        if order.items.filter(item__slug = item.slug).exists():
            order_item.quantity = order_item.quantity+1
            order_item.save()
            messages.info(request,"This item quantity is updated in your cart.")
            return redirect("core:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request,"This item was added to your cart.")
            return redirect("core:order-summary")
    else:
        #if order not exists then create Order nd add item to your cart
        ordered_date=timezone.now()
        order=Order.objects.create(user=request.user,ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request,"This item was added to your cart.")
        return redirect("core:order-summary")
    
@login_required
def remove_from_cart(request,slug):
    item=get_object_or_404(Item,slug=slug)#take the item of product
    order_qs= Order.objects.filter(
        user=request.user,
        ordered=False
        )#create item as OrderItem
    
    if order_qs.exists():# if order exists
        order=order_qs[0] #selects first one 
        # check if order item is in the order
        if order.items.filter(item__slug = item.slug).exists():
            order_item=OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            #remove the order_item from order.items
            order.items.remove(order_item)
            #delete the order_item so that is deleted in all orders,order_item
            order_item.delete()
            messages.info(request,"This item was removed from  your cart.")
            return redirect("core:order-summary")
        else:
            messages.info(request,"This item was not in your cart.")
            return redirect("core:product",slug=slug)
    else:
        messages.info(request,"You do not have an active order")
        return redirect("core:product",slug=slug)

@login_required
def remove_single_from_cart(request,slug):
    item=get_object_or_404(Item,slug=slug)#take the item of product
    order_qs= Order.objects.filter(
        user=request.user,
        ordered=False
        )#create item as OrderItem
    
    if order_qs.exists():# if order exists
        order=order_qs[0] #selects first one 
        # check if order item is in the order
        if order.items.filter(item__slug = item.slug).exists():
            order_item=OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity>1:
                order_item.quantity = order_item.quantity-1
                order_item.save()
            #remove the order_item from order.items
            else:
                #remove the order_item from order.items
                order.items.remove(order_item)
                #delete the order_item so that is deleted in all orders,order_item
                order_item.delete()
            messages.info(request,"This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request,"This item was not in your cart.")
            return redirect("core:order-summary ")
    else:
        messages.info(request,"You do not have an active order")
        return redirect("core:order-summary")
    
def get_coupon(request,code):
    try:
        coupon=Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:      
        messages.info(request,"This coupon does not exist")
        return redirect("core:checkout")
class AddCouponView(View):
    def post(self,*args,**kwargs):
        try:
            form=CouponForm(self.request.POST or None)
            if form.is_valid():
                try:
                    code=form.cleaned_data.get('code')
                    order=Order.objects.get(user=self.request.user,ordered=False)
                    order.coupon=get_coupon(self.request,code)
                    order.save()
                    messages.success(self.request,"Succesfully added coupon")
                    return redirect("core:checkout")
                except ObjectDoesNotExist:      
                    messages.info(self.request,"You do not have an active order")
                    return redirect("core:checkout")
        except Exception as e:
            return redirect('core:checkout')
        
class RequestRefundView(View):
    def get(self,*args,**kwargs):
        form=RefundForm()
        context={
            'form':form
        }
        return render(self.request,"request_refund.html",context)
    def post(self,*args,**kwargs):
        form=RefundForm(self.request.POST)
        if form.is_valid():
            ref_code=form.cleaned_data['ref_code']
            message=form.cleaned_data['message'] 
            email=form.cleaned_data['email']
            #edit the order
            try:
                order=Order.objects.get(ref_code=ref_code)
                order.refund_requested=True
                order.save()
                #store the refund
                refund=Refund()
                refund.order=order
                refund.reason=message
                refund.email=email
                refund.save()
                print('exec.')#order does exist
                messages.info(self.request,"Your request was received")
                return redirect("core:request-refund")
            except ObjectDoesNotExist:
                print('error')#order does not exist
                messages.info(self.request,"This object does not exist.")
                return redirect("core:request-refund")








