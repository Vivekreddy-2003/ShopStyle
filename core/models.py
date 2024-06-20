from django.db.models.signals import post_save
from django.conf import settings
from django.utils import timezone
from django.db import models
from django.shortcuts import reverse
from django_countries.fields import CountryField
CATEGORY_CHOICES=(
    ('shirt','shirt'),
    ('shorts','shorts'),
    ('outwear','outwear'),
    ('shoes','shoes'),
    ('bats','bats'),
    ('t-shirts','t-shirts'),
    ('bags','bags'),
    ('pants','pants'),
    ('accessories','accessories'),
)
LABEL_CHOICES=(
    ('P','primary'),
    ('S','secondary'),
    ('D','danger'),
    ('PU','Puma'),
)
ADDRESS_CHOICES=(
    ('B','Billing'),
    ('S','Shipping'),
    
)
SIZE_LABELS=(
    ('S','28'),
    ('M','30'),
    ('L','40'),
    ('XL','42'),
    ('XXL','44')
)
GENDER_LABELS=(
    ('men','men'),
    ('boys','boys')
)
def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)

post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

# Create your models here.
class Item(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,blank=True,null=True)
    title=models.CharField(max_length=100)
    price=models.FloatField()
    size=models.CharField(choices=SIZE_LABELS,max_length=5,default=True)
    discount_price=models.FloatField(default=8.0,blank=True,null=True)
    gender=models.CharField(choices=GENDER_LABELS,max_length=5,default='men')
    category=models.CharField(choices=CATEGORY_CHOICES,max_length=64,default=True)
    label=models.CharField(choices=LABEL_CHOICES,max_length=64,default=True)
    slug=models.SlugField(null=True) 
    description = models.TextField(max_length=255, default='This is Text  Description')
    image=models.ImageField(blank=True,null=True)
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("core:product",kwargs={
            'slug':self.slug
        })
    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart",kwargs={
            'slug':self.slug
        })
    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart",kwargs={
            'slug':self.slug
        })

class OrderItem(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,blank=True,null=True)
    ordered=models.BooleanField(default=False) 
    item=models.ForeignKey(Item,on_delete=models.CASCADE)
    quantity=models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f" {self.quantity} of {self.item.title}"
    
    def get_total_item_price(self):
        return self.quantity * self.item.price
    
    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price
        
    
    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()
    
    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()
    
    def get_name(self):
        return self.item.name

class Order(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE) 
    ref_code=models.CharField(max_length=20,default=123,blank=True,null=True)
    items=models.ManyToManyField(OrderItem)
    start_date=models.DateTimeField(auto_now_add=True)
    ordered_date=models.DateTimeField(auto_now_add=True)
    ordered=models.BooleanField(default=False)
    shipping_address=models.ForeignKey('Address',related_name='shipping_address',on_delete=models.SET_NULL,blank=True,null=True)
    billing_address=models.ForeignKey('Address',related_name='billing_address',on_delete=models.SET_NULL,blank=True,null=True)
    payment=models.ForeignKey('Payment',on_delete=models.SET_NULL,blank=True,null=True)
    coupon=models.ForeignKey('Coupon',on_delete=models.SET_NULL,blank=True,null=True)
    being_delivered=models.BooleanField(default=False)
    received=models.BooleanField(default=False)
    refund_requested=models.BooleanField(default=False)
    refund_granted=models.BooleanField(default=False)
    coupon_amount=models.FloatField(default=5.0)

    def order_date(self):
        return self.ordered_date

    '''
    1.Item added to Cart
    2.Added a billing address
    (Falied Checkout)
    3.Payment
    (PreProcessing,processing,packaging etc.)
    4.Being delivered
    5.Received
    6.Refunds
    '''
    def __str__(self):
        return self.user.username
    def get_coupon_name(self):
        if self.coupon:
            return self.coupon.code
    def get_coupon(self):
        if self.coupon:
            return self.coupon.amount
        
    def get_total(self):
        total=0
        for order_item in self.items.all():
            total+=order_item.get_final_price()
        if self.coupon:
            total-=self.coupon.amount
            if total < 0:
                total=0
        return total
    def whole_total(self):
        total=0
        for order_item in self.items.all():
            total+=order_item.get_final_price()
        return total
class Address(models.Model):
    user= models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,blank=True,null=True)
    street_address=models.CharField(max_length=10000,null=True, blank=True)
    apartment_address=models.CharField(max_length=10000,null=True, blank=True)
    country=CountryField(multiple=False,null=True, blank=True)
    zip=models.CharField(max_length=100,null=True, blank=True)
    address_type=models.CharField(max_length=1,choices=ADDRESS_CHOICES)
    default=models.BooleanField(default=False)
    def ship_address(self):
        return self.street_address
    def __str__(self):
        if self.user:
            return self.user.username
        else:
            return "No User"

    class Meta:
        verbose_name_plural='Adresses'
class Payment(models.Model):
    stripe_charge_id=models.CharField(max_length=50)
    user= models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,blank=True,null=True)
    amount=models.FloatField()
    timestamp=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    def get_payment_id(self):
        return self.stripe_charge_id
    def get_amount(self):
        return self.amount
class Coupon(models.Model):
    code =models.CharField(max_length=15)
    amount=models.FloatField(default=5.0)
    def __str__(self):
        return self.code
    
class Refund(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE)
    reason=models.TextField()
    accepted=models.BooleanField(default=False)
    email=models.EmailField()
    def __str__(self):
        return f"{ self.pk}"
    
