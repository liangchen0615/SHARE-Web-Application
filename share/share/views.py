import openpyxl
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.db import transaction
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from share.forms import LoginForm, RegisterForm, SearchForm, ProfileForm, FileForm, AddressForm
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.core import serializers
from share.models import Profile, Item, CartItem, Cart, Order, OrderItem, Question, Answer, Review, ReviewFile, Coupon, Address


from email.mime.image import MIMEImage
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.contrib.staticfiles import finders
from django.db.models import Avg
import json



def load_item():
    sheet = openpyxl.load_workbook("item_stream.xlsx").active
    coupon1 = Coupon(code = 'FARNAM', discount = 0.1)
    coupon2 = Coupon(code = 'LOVE WEBAPPS', discount = 0.8)
    coupon1.save()
    coupon2.save()
    for row in sheet.iter_rows(min_row=2):
        title = row[0].value
        if title == "" or title is None:
            continue
        desc = row[1].value
        pic = row[2].value
        type = row[3].value
        content_type = row[4].value
        seller = row[5].value
        price = row[6].value
        stock = row[7].value
        averagerating = 0
        item = Item(title=title, description=desc, picture=pic, type=type, content_type=content_type, price=price,
                    stock=stock, averagerating = averagerating)
        item.save()


def home(request):
    # load_item()
    return redirect(reverse('productStream'))


def login_action(request):
    if request.method == 'GET':
        loginForm = LoginForm()
        context = {'form': loginForm}
        return render(request, 'share/login.html', context)

    form = LoginForm(request.POST)
    context = {'form': form}

    if not form.is_valid():
        return render(request, 'share/login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)
    return redirect(reverse('home'))


def logout_action(request):
    logout(request)
    return render(request, 'share/login.html', {'form': LoginForm()})


def register_action(request):
    context = {}

    if request.method == 'GET':
        context['form'] = RegisterForm()
        return render(request, 'share/register.html', context)

    form = RegisterForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        return render(request, 'share/register.html', context)

    new_user = User.objects.create_user(
        username=form.cleaned_data['username'],
        password=form.cleaned_data['password'],
        email=form.cleaned_data['email'],
        first_name=form.cleaned_data['first_name'],
        last_name=form.cleaned_data['last_name']
    )

    new_profile = Profile()
    new_profile.user = new_user
    new_profile.save()

    new_cart = Cart()
    new_cart.user = new_user
    new_cart.save()
    new_user.save()
    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    # Generate a one-time use token and an email message body
    token = default_token_generator.make_token(new_user)
    email_body = """
    Please click the link below to verify your email address and complete the registration of your account:
    http://{host}{path}
    """.format(host=request.get_host(),
               path=reverse('confirm', args=(new_user.username, token)))

    send_mail(subject="Verify your email address",
              message=email_body,
              from_email="yueminga@andrew.cmu.edu",
              recipient_list=[new_user.email])
    context['email'] = form.cleaned_data['email']
    return render(request, 'share/needs-confirmation.html', context)
    # login(request, new_user)
    # return redirect(reverse('home'))


def confirm_action(request, username, token):
    user = get_object_or_404(User, username=username)

    # Send 404 error if token is invalid
    if not default_token_generator.check_token(user, token):
        raise Http404

    # Otherwise token was valid, activate the user.
    user.is_active = True
    user.save()

    return render(request, 'share/confirmed.html', {})

def product_stream_action(request):
    types = Item.objects.all().values("type").distinct()
    print(request.GET)
    selectedType =""
    if request.method == 'GET':
        searchResult = Item.objects
        if request.GET.get('type'):
            type = request.GET['type']
            if type != "":
                selectedType=type
                searchResult = Item.objects.filter(type=type)
        elif request.GET.get('selected_type'):
            type = request.GET['selected_type']
            if type != "":
                selectedType = type
                searchResult = Item.objects.filter(type=type)
        if request.GET.get('order'):
            order = request.GET.get('order')
            try:
                int(order)
                if int(order) == 1:
                    searchResult = searchResult.order_by('price').reverse()
                else:
                    searchResult = searchResult.order_by('price')
            except:
                pass
        if request.GET.get('searchTerm'):
            searchTerm = request.GET['searchTerm']
            if searchTerm != "":
                searchResult = Item.objects.filter(title__icontains=searchTerm)
        searchResult = searchResult.all()
        context = {'items':searchResult, 'types': types, 'selected_type': selectedType}
        return render(request, 'share/productStream.html', context)


def product_detail_action(request, id):
    item_to_display = get_object_or_404(Item, id=id)
    questions = Question.objects.filter(item=item_to_display)
    reviews = Review.objects.filter(item=item_to_display).order_by("-creation_time")
    all_files = ReviewFile.objects.all()
    rating_sum = 0
    review_count = 0
    for review in reviews:
        rating_sum += review.rating
        review_count += 1
    if review_count == 0:
        averagerating = 0.0
    else:
        averagerating = rating_sum / review_count
    item_to_display.averagerating = averagerating
    item_to_display.save()
    return render(request, 'share/productDetail.html', {'item': item_to_display, 'questions': questions, 'reviews': reviews, 'rating': averagerating, 'all_files': all_files})
    # if request.method == 'POST':
    #     question_content = request.POST['question']
    #     question = Question(user=request.user, item=item_to_display, text=question_content)
    #     question.save()
    #     questions = Question.objects.filter(item=item_to_display)
    #     return render(request, 'share/productDetail.html', {'item': item_to_display, 'questions': questions, 'reviews': reviews, 'rating': averagerating})


def productPicture(request, id):
    item = get_object_or_404(Item, id=id)

    # Maybe we don't need this check as form validation requires a picture be uploaded.
    # But someone could have delete the picture leaving the DB with a bad references.
    if not item.picture:
        raise Http404

    return HttpResponse(item.picture, content_type=item.content_type)

@login_required
def cart_action(request):
    try:
        request.user.cart
    except:
        new_cart = Cart()
        new_cart.user = request.user
        new_cart.save()
    print(request.user.cart.cart_items.all().values())
    return render(request, 'share/cart.html', {'cart': request.user.cart.cart_items.all()})

@login_required(login_url='login')
def add_to_cart_action(request, id):
    item = get_object_or_404(Item, id=id)
    questions = Question.objects.filter(item=item)
    print(request.POST)
    if 'cart_amount' not in request.POST or not request.POST['cart_amount']:
        return redirect(reverse('productDetail', args=(id,)))
    try:
        item_amount = int(request.POST['cart_amount'])
    except:
        pass
    if item_amount > item.stock or item.stock <= 0:
        return render(request, 'share/productDetail.html', {'item': item, 'questions': questions, 'message': 'Out of stock'})
    for cart_item in request.user.cart.cart_items.all():  #already exist same item, need to update quantity
        if cart_item.item.id == item.id:
            cart_item.quantity = cart_item.quantity + item_amount
            cart_item.save()
            request.user.cart.save()
            return redirect(reverse('productDetail', args=(id,)))

    # create new item
    new_cart_item = CartItem(user=request.user, item=item, quantity=item_amount, items_price=item.price, cart=request.user.cart)
    new_cart_item.save()
    request.user.cart.cart_items.add(new_cart_item)
    request.user.cart.save()
    return redirect(reverse('productDetail', args=(id,)))


@login_required
def profile_action(request):
    context = {}
    if request.method == 'GET':
        context['form'] = AddressForm()
        addresses = Address.objects.filter(user=request.user)
        context['addresses'] = addresses
        return render(request, 'share/profile.html', context)

    form = AddressForm(request.POST)
    context['form'] = form
    addresses = Address.objects.filter(user=request.user)
    context['addresses'] = addresses

    if not form.is_valid():
        return render(request, 'share/profile.html', context)

    new_address = Address()
    user=request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
    new_address.user=user
    new_address.name=form.cleaned_data['name']
    new_address.address1=form.cleaned_data['address1']
    new_address.address2=form.cleaned_data['address2']
    new_address.zip_code=form.cleaned_data['zip_code']
    new_address.city=form.cleaned_data['city']
    new_address.country=form.cleaned_data['country']

    
    new_address.save()

    return render(request, 'share/profile.html', context)


@login_required
def checkout_action(request):
    context = {}
    keys = request.POST.keys()
    total_price = 0
    cart = Cart.objects.filter(user=request.user).first()
    cart_items = CartItem.objects.filter(user=request.user)
    out = False

    for key in keys:
        if "item_quantity" in key:
            quantity = request.POST.get(key)
            item_id = key[len("item_quantity_"):]
            item = get_object_or_404(Item, id=item_id)
            cart_item = CartItem.objects.filter(id=item_id).first()
            if cart_item is not None:
                try:
                    cart_item.quantity = float(quantity)
                except:
                    cart_item.quantity = 1
                cart_item.save()
                total_price += cart_item.quantity * cart_item.items_price
    cart.total_price = total_price
    cart.total_price = round(total_price, 2)
    cart.save()
    context['cart'] = cart
    context['form'] = AddressForm()
    addresses = Address.objects.filter(user=request.user)
    context['addresses'] = addresses
    for cartitem in cart_items:
        if cartitem.quantity > cartitem.item.stock:
            out = True
            cartitem.quantity = cartitem.item.stock
            cartitem.save()
    if out is True:
        context['cart'] = request.user.cart.cart_items.all()
        context['message'] = 'Product out of stock'
        return render(request, 'share/cart.html', context)

    context['form'] = AddressForm()
    addresses = Address.objects.filter(user=request.user)
    context['addresses'] = addresses
    context['error'] = "You must have an address to place order"
    return render(request, 'share/address.html', context)

@login_required()
def add_addr_action(request):
    context={}
    form = AddressForm(request.POST)
    context['form'] = form
    addresses = Address.objects.filter(user=request.user)
    context['addresses'] = addresses

    if not form.is_valid():
        return render(request, 'share/address.html', context)

    context['error'] = "You must have an address to place order"

    new_address = Address()
    user = request.user._wrapped if hasattr(request.user, '_wrapped') else request.user
    new_address.user = user
    new_address.name = form.cleaned_data['name']
    new_address.address1 = form.cleaned_data['address1']
    new_address.address2 = form.cleaned_data['address2']
    new_address.zip_code = form.cleaned_data['zip_code']
    new_address.city = form.cleaned_data['city']
    new_address.country = form.cleaned_data['country']

    new_address.save()

    return render(request, 'share/address.html', context)

@login_required
def place_order_action(request):
    cart = get_object_or_404(Cart, user=request.user)
    context = {}
    context['cart'] = cart

    if not 'address' in request.POST or not request.POST['address']:
        context['error'] = "You must have an address to place order"
        return render(request, 'share/checkout.html', context)
    address_id = request.POST['address']
    print(address_id)
    address = get_object_or_404(Address, id=address_id)
    print(address)
    context['address'] = address
    return render(request, 'share/checkout.html', context)

def logo_data():
    with open(finders.find('share/share.png'), 'rb') as f:
        logo_data = f.read()
    logo = MIMEImage(logo_data)
    logo.add_header('Share.com', '<logo>')
    return logo


@login_required
def complete_action(request):
    context = {}
    address_id = -1
    if request.method == "POST":
        import json
        post_data = json.loads(request.body.decode("utf-8"))
        print(post_data)
        try:
            address_id = int(post_data['address_id'])
        except:
            return _my_json_error_response("You must choose an address to add.", status=400)
    if request.method == 'GET':
        return render(request, 'share/cart.html', context)
    print(address_id)
    new_order = Order()
    new_order.user = request.user
    if not request.user.cart.coupon:
        new_order.total_price = request.user.cart.total_price
    else:
        new_order.total_price = request.user.cart.total_price * request.user.cart.coupon.discount
    new_order.total_price = round(new_order.total_price, 2)
    address = get_object_or_404(Address, id=address_id)
    new_order.address = address
    new_order.save()
    for cart_item in request.user.cart.cart_items.all():
        order_item = OrderItem()
        order_item.order = new_order
        order_item.user = request.user
        order_item.item = cart_item.item
        order_item.quantity = cart_item.quantity
        order_item.items_price = cart_item.items_price
        order_item.save()
        item = order_item.item
        item.stock = item.stock - order_item.quantity
        item.save()
    cart = get_object_or_404(Cart, user=request.user)
    cart.total_price = 0
    cart.coupon = None;
    cart.save()
    CartItem.objects.filter(user = request.user).delete()
    email_body = """
    Thank you for shopping at Share. Your order information list below:
    Your order ship to {order_receiver}
    Your order date is {order_time}
    Your order price is ${order_price}
    Your order address is {order_address}
    """.format(order_time=new_order.datetime,
               order_price=new_order.total_price,
               order_receiver = new_order.user.first_name + ' ' + new_order.user.last_name,
               order_address = new_order.address.address1 + ', ' + new_order.address.address2 + ', ' + new_order.address.city
                + ', ' + new_order.address.zip_code)
    message = EmailMultiAlternatives(
        subject="Your Share.com Order Confirmation",
        body=email_body,
        from_email="yueminga@andrew.cmu.edu",
        to=[request.user.email],
    )
    message.mixed_subtype = 'related'
    message.attach(logo_data())

    message.send(fail_silently=False)
    context['email'] = request.user.email
    return render(request, 'share/checkout.html', context)

def _my_json_error_response(message, status=200):
    response_json = '{ "error": "' + message + '" }'
    return HttpResponse(response_json, content_type='application/json', status=status)

def get_product_json_dumps_serializer(request, id):
    #id is item.id
    if not request.user.id:
        return _my_json_error_response("You must use a POST request with a login require", status=401)
    response_question = []
    response_answer = []
    for question in Question.objects.all():
        if question.item.id == id:
            item_question = {
                'id': question.id,
                'text': question.text,
                'creation_time': question.creation_time.isoformat(),
                'user': question.user.get_full_name(),
                'item_id': question.item.id,
                'user_id': question.user.id,
            }
            response_question.append(item_question)

    #print(Comment.objects.all())
    for answer in Answer.objects.all():
        if answer.item.id == id:
            item_answer = {
                'id': answer.id,
                'text': answer.text,
                'creation_time': answer.creation_time.isoformat(),
                'user': answer.user.get_full_name(),
                'question_id': answer.question.id,
                'item_id': answer.item.id,
                'user_id': answer.user.id,
            }
            response_answer.append(item_answer)

    response_data = {'questions': response_question, 'answers': response_answer, 'item_id': id}
    #print(response_data)
    response_json = json.dumps(response_data)

    response = HttpResponse(response_json, content_type='application/json')
    response['Access-Control-Allow-Origin'] = '*'
    return response

@login_required
def post_question_action(request, id):
    if not request.user.id:
        return _my_json_error_response("You must use a POST request with a login require", status=401)
    if request.method == 'GET':
        return _my_json_error_response("You must use a POST request for this operation", status=405)
    if not 'csrfmiddlewaretoken' in request.POST or not request.POST['csrfmiddlewaretoken']:
        return _my_json_error_response("You must use a POST request for this operation", status=403)
    if not 'question_text' in request.POST or not request.POST['question_text']:
        return _my_json_error_response("You must enter a answer to add.", status=400)

    item = get_object_or_404(Item, id=id)
    new_question = Question(text = request.POST['question_text'], user = request.user,
                        creation_time = timezone.now(), item = item)
    new_question.save()
    return get_product_json_dumps_serializer(request, id)

@csrf_exempt
def post_answer_action(request, id):
    #id is item.id
    if not request.user.id:
        return _my_json_error_response("You must use a POST request with a login require", status=401)
    if request.method == 'GET':
        return _my_json_error_response("You must use a POST request for this operation", status=405)
    if not 'csrfmiddlewaretoken' in request.POST or not request.POST['csrfmiddlewaretoken']:
        return _my_json_error_response("You must use a POST request for this operation", status=403)
    if not 'answer_text' in request.POST or not request.POST['answer_text']:
        return _my_json_error_response("You must enter a answer to add.", status=400)
    if not 'question_id' in request.POST or not request.POST['question_id']:
        return _my_json_error_response("You must enter a answer to add.", status=400)

    try:
        val = int(request.POST.get('question_id'))
    except ValueError:
        return _my_json_error_response("Invalid type of post_id", status=400)
    try:
        q = Question.objects.get(id=request.POST['question_id'])
    except Question.DoesNotExist:
        return _my_json_error_response("Invalid question_id", status=400)

    question = get_object_or_404(Question, id=request.POST.get('question_id'))
    item = get_object_or_404(Item, id=id)
    new_answer = Answer(text = request.POST['answer_text'], user = request.user,
                          creation_time = timezone.now(), question = question, item = item)
    new_answer.save()
    return get_product_json_dumps_serializer(request, id)



@login_required
def order_history_action(request):
    orders = Order.objects.filter(user=request.user)
    order_items = OrderItem.objects.filter(user=request.user)
    return render(request, 'share/orderHistory.html', {"orders": orders.order_by('-datetime'), "orderitems": order_items})

def review_detail_action(request, id):
    #id is orderitem.id
    order_item = get_object_or_404(OrderItem, id=id)
    if request.method == 'GET':
        form = FileForm()
        return render(request, 'share/reviewDetail.html', {'orderitem': order_item, 'form': form})
    return render(request, 'share/reviewDetail.html', {'orderitem': order_item})

@login_required
def review_action(request, id):
    #id is orderitem.id
    order_item = get_object_or_404(OrderItem, id=id)
    order = order_item.order
    if 'review' in request.POST:
        new_reivew = Review()
        new_reivew.user = request.user
        new_reivew.item = order_item.item
        new_reivew.creation_time = timezone.now()
        if 'review' in request.POST:
            new_reivew.text = request.POST['review']
        if 'rating' in request.POST:
            new_reivew.rating = request.POST['rating']
        form = FileForm(request.POST, request.FILES)
        files = request.FILES.getlist('files')
        if form.is_valid():
            new_reivew.save()
            order_item.review = new_reivew
            order_item.save()
            for f in files:
                file_instance = ReviewFile(files=f, review = new_reivew, content_type = f.content_type)
                file_instance.save()
        else:
            print(form)
            return render(request, 'share/reviewDetail.html', {'orderitem': order_item, 'form': form})



    return render(request, 'share/reviewDetail.html', {'orderitem': order_item,'form':form})


def delete_cartitem_action(request):
    if request.method == 'POST' and 'id' in request.POST:
        id = request.POST['id']
        CartItem.objects.filter(user=request.user, id=id).delete()
    return render(request, 'share/cart.html', {'cart': request.user.cart.cart_items.all()})

def order_detail_action(request, id):
    #id is order.id
    order = get_object_or_404(Order, id=id)
    order_items = OrderItem.objects.filter(order=order)
    return render(request, 'share/orderDetail.html', {'orderitems': order_items, 'order': order})

def photo_action(request, id):
    reviewFile = get_object_or_404(ReviewFile, id=id)
    print('Picture #{} fetched from db: {} (type={})'.format(id, reviewFile.files, type(reviewFile.files)))
    if not reviewFile.files:
        raise Http404

    return HttpResponse(reviewFile.files, content_type=reviewFile.content_type)

def coupon_action(request):
    coupon_text = request.POST['coupon_text']
    coupons = Coupon.objects.all()
    cart = request.user.cart
    for coupon in coupons:
        if coupon_text == coupon.code:
            cart.coupon = coupon
            cart.save()
            break
    cart = request.user.cart.cart_items.all()
    return render(request, 'share/cart.html', {'cart': cart})
