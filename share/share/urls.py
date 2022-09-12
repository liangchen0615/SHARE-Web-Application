from django.urls import path
from share import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login', views.login_action, name='login'),
    path('register', views.register_action, name='register'),
    path('logout', views.logout_action, name='logout'),
    path('global', views.product_stream_action, name='global'),
    path('cart', views.cart_action, name='cart'),
    path('profile', views.profile_action, name='profile'),
    path('addtocart/<int:id>', views.add_to_cart_action, name='addtocart'),
    path('productDetail/<int:id>', views.product_detail_action, name='productDetail'),
    # need three new actions
    path('itemPicture/<int:id>', views.productPicture, name='productPicture'),
    path('productStream',views.product_stream_action,name='productStream'),
    path('checkout', views.checkout_action, name="checkout" ),
    path('complete', views.complete_action, name="complete"),
    path('post_question/<int:id>', views.post_question_action, name="post_question"),
    path('post_answer/<int:id>', views.post_answer_action, name="post_answer"),
    path('orderHistory', views.order_history_action, name="orderHistory"),
    path('confirm-registration/<slug:username>/<slug:token>', views.confirm_action, name='confirm'),
    path('order_detail/<int:id>', views.order_detail_action, name="order_detail"),
    path('delete_cartitem', views.delete_cartitem_action, name="delete_cartitem"),
    path('reviewDetail/<int:id>', views.review_detail_action, name="reviewDetail"),
    path('review/<int:id>', views.review_action, name="review"),
    path('placeOrder', views.place_order_action, name='placeOrder'),
    path('get_product/<int:id>', views.get_product_json_dumps_serializer, name='get_product'),
    path('photo/<int:id>', views.photo_action, name='photo'),
    path('coupon', views.coupon_action, name='coupon'),
    path('add_addr', views.add_addr_action, name='add_addr'),
]