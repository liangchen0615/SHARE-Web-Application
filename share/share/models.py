from datetime import datetime
from re import X
from socket import AddressInfo
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django_countries.fields import CountryField

class Provider(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)


class Item(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    picture = models.FileField(blank=True)
    content_type = models.CharField(max_length=50, blank=True, null=True)
    seller = models.OneToOneField(Provider, on_delete=models.PROTECT, related_name="selling", blank=True, null=True)
    price = models.FloatField(default=0.0)
    type = models.CharField(max_length=100, blank=True, null=True)
    stock = models.IntegerField(default=0)
    averagerating = models.FloatField(default=0)

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="post_creators")
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    creation_time = models.DateTimeField(default=datetime.now().strftime("%Y-%m-%d %H:%M"))
    text = models.CharField(max_length = 200)
    picture = models.FileField(blank=True)
    rating = models.FloatField(default=0)

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    name = models.CharField("Full name", max_length=1024)
    address1 = models.CharField("Address line 1", max_length=1024)
    address2 = models.CharField("Address line 2", max_length=1024)
    zip_code = models.CharField("ZIP / Postal code", max_length=12)
    city = models.CharField("City", max_length=1024)
    country = CountryField(multiple=False)
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    datetime = models.DateTimeField(default=datetime.now().strftime("%Y-%m-%d %H:%M"))
    total_price = models.FloatField(default=0.0)
    address = models.ForeignKey(Address, on_delete=models.PROTECT)

class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=0)
    items_price = models.FloatField(default=0.0)
    review = models.OneToOneField(Review, on_delete=models.PROTECT, blank=True, null=True)


class Customer(models.Model):
    orders = models.ManyToManyField(Order, related_name="buyers")
    following = models.ManyToManyField(User, related_name="followers")


class Media(models.Model):
    title = models.CharField(max_length=200)
    content = models.FileField(blank=True)
    content_type = models.CharField(max_length=50)
    datetime = models.DateTimeField(default=datetime.now().strftime("%Y-%m-%d %H:%M"))
    uploader = models.ForeignKey(User, on_delete=models.PROTECT)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name='profile')
    bio_text = models.CharField(max_length=200)
    picture = models.FileField(blank=True)
    content_type = models.CharField(max_length=50)

class Coupon(models.Model):
    code = models.CharField(max_length = 20)
    discount = models.FloatField(default=0.0)

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name='cart')
    total_price = models.FloatField(default=0.0)
    coupon = models.ForeignKey(Coupon, on_delete=models.PROTECT, blank=True, null=True)

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=0)
    items_price = models.FloatField(default=0.0)
    cart = models.ForeignKey(Cart,on_delete=models.PROTECT, related_name='cart_items')



class Question(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="question_user")
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    creation_time = models.DateTimeField(default=datetime.now().strftime("%Y-%m-%d %H:%M"))
    text = models.CharField(max_length = 200)

class Answer(models.Model):
    text  = models.CharField(max_length = 200)
    creation_time  = models.DateTimeField(default=datetime.now().strftime("%Y-%m-%d %H:%M"))
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    creation_time = models.DateTimeField(default=datetime.now().strftime("%Y-%m-%d %H:%M"))
    text = models.CharField(max_length = 200)
    rating = models.FloatField(default=0)

class ReviewFile(models.Model):
    files = models.FileField(blank=True)
    content_type = models.CharField(max_length=50)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)



