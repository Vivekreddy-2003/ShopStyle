from django.urls import path
from  .views import(
    ItemDetailView,
    #login,
    #register,
    OrderSummaryView,
    remove_single_from_cart,
    CheckoutView,
    add_to_cart,
    remove_from_cart,
    AddCouponView,
    RequestRefundView,
    PaymentView,
    apply_filters,
    detail_Category,
    DeleteAddressView,
    carousel_item,
    detail_puma,
    profile,
   HomeView,
   carousel_filter,
   
)
app_name='core'
urlpatterns=[
    
    path('',HomeView.as_view(),name='home'),
    path('carousel-filter/',carousel_filter,name='carousel-filter'),
    path('puma/',detail_puma,name='puma'),
    path('carousel_item/',carousel_item,name='carousel_item'),
    path('delete_address',DeleteAddressView.as_view(),name='delete_address'),
    path('profile/',profile,name='profile'),
    path('detail/', detail_Category, name='detail'),
    path('apply_filters/', apply_filters, name='apply_filters'),
    path('checkout/',CheckoutView.as_view(),name='checkout'),
    path('order-summary/',OrderSummaryView.as_view(),name='order-summary'),
    path("product/<slug>/",ItemDetailView.as_view(),name="product"),
    path("add-to-cart/<slug>/",add_to_cart,name="add-to-cart"),
    path("add-coupon/",AddCouponView.as_view(),name="add-coupon"),
    path("remove-from-cart/<slug>/",remove_from_cart,name="remove-from-cart"),
    path("remove-single-from-cart/<slug>/",remove_single_from_cart,name="remove-single-from-cart"),
    path('payment/<payment_option>',PaymentView.as_view(),name='payment'),
    path('request-refund',RequestRefundView.as_view(),name='request-refund')
]