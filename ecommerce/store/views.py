from django.shortcuts import render, redirect
from .models import*
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
import datetime
from .authentication import valid,SendMailWithHtml,senddeliverymail
from random import randint

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.template.loader import render_to_string

# Create your views here.


@csrf_exempt
def updateItem(request):
    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(user=request.user)
        customer.save()
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        order.save()
    else:
        if "orderId" in request.session:
            try:
                order = Order.objects.get(pk=request.session["orderId"])
                print("order found")
            except:
                order = Order(complete=False)
                order.save()
                request.session["orderId"] = order.id
                print("couln't find order")
        else:
            order = Order(complete=False)
            order.save()
            request.session["orderId"] = order.id

            print("created new order")

    try:
        data = json.loads(request.body)

    except:
        return JsonResponse("couldn't add item error-code:1", safe=False)

    productID = data['productID']
    action = data["action"]
    print(productID, action, request.user)

    product = Product.objects.get(pk=productID)

    orderItem, created = OrderItem.objects.get_or_create(
        product=product, order=order)

    if not created:
        if action == "add":
            orderItem.quantity += 1
            msg = "item added"
        elif action == "remove":
            orderItem.quantity -= 1
            msg = "item removed"

    if orderItem.quantity == 0:
        order.orderitem_set.remove(orderItem)
        print("removed")

        orderItem.delete()
        order.save()
        return JsonResponse("Item deleted", safe=False)

    orderItem.save()

    return JsonResponse(msg, safe=False)


def store(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
    else:
        if "orderId" in request.session:
            try:
                order = Order.objects.get(pk=request.session["orderId"])
                print("order found")
            except:
                order = Order(complete=False)
                order.save()
                request.session["orderId"] = order.id
                print("couln't find order")
        else:
            order = Order(complete=False)
            order.save()
            request.session["orderId"] = order.id
            print("created new order")
            if "completed_orders" not in request.session:
                request.session["completed_orders"] = []

    products = Product.objects.all()
    context = {"products": products, "order": order}
    return render(request, "store/store.html", context)


def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)

    else:
        if "orderId" in request.session:
            try:
                order = Order.objects.get(pk=request.session["orderId"])
                print("order found")
            except:
                order = Order(complete=False)
                order.save()
                request.session["orderId"] = order.id
                print("couln't find order")
        else:
            order = Order(complete=False)
            order.save()
            request.session["orderId"] = order.id
            print("created new order")

    items = order.orderitem_set.all()
    context = {"items": items, "order": order}
    return render(request, "store/cart.html", context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)

    else:
        if "orderId" in request.session:
            try:
                order = Order.objects.get(pk=request.session["orderId"])
            except:
                redirect("/")
        else:
            redirect("/")

    items = order.orderitem_set.all()
    if len(items)==0:
        return store(request)
    context = {"items": items, "order": order}
    return render(request, "store/checkout.html", context)


def submitorder(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(
                customer=customer, complete=False)

        else:

            customer, created = Customer.objects.get_or_create(
                name=request.POST["name"], email=request.POST["email"])
            customer.save()
            order = Order.objects.get(pk=request.session["orderId"])
            order.customer = customer
            order.save()

        print(order.orderitem_set.all())
        order.total = order.total_amount
        order.transaction_id = datetime.datetime.now().timestamp()
        shippingAddress = ShippingAddress(
            customer=customer,
            order=order,
            address=request.POST["address"],
            city=request.POST["city"],
            state=request.POST["state"],
            zipcode=request.POST["zipcode"],
            country=request.POST["country"]
        )
        order.complete = True
        order.save()

        shippingAddress.save()
        html = render_to_string("email/order2.html",{"ship":shippingAddress})
        SendMailWithHtml(customer.email,html,"Order Received")
        # sendemail(customer.email,text,"Order received")
        html = render_to_string("email/delivered.html",{"ship":shippingAddress})
        senddeliverymail(customer.email,html)
        if not request.user.is_authenticated:
            request.session["completed_orders"].append(
                request.session["orderId"])
            print("completed order :", request.session["completed_orders"])
            del request.session["orderId"]
        
    return redirect("/")


def register(request, error="", success="", con={}):
    if not request.user.is_authenticated:
        if request.method == "GET":
            context = {"error": error, "success": success}
            context.update(con)
            return render(request, "registration/register.html", context)
        else:
            form = UserCreationForm(request.POST)
            if form.is_valid() and "email" in request.session and "name" in request.session:
                form.save()
                name = str(request.session["name"])
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=raw_password)
                login(request, user)

                customer = Customer.objects.create(
                    user=user, name=name, email=request.session["email"])
                return redirect("/")
            request.method = "GET"
            return register(request, error=form.errors)
        redirect("/register")
    return redirect("/")


def loginView(request, error=""):
    if not request.user.is_authenticated:
        if request.method == "GET":
            return render(request, "registration/login.html", {"error": error})

        else:
            P = request.POST
            if "username" in P and "password" in P:
                username = P["username"]
                password = P["password"]
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect("/")
                else:
                    request.method = "GET"
                    return loginView(request, error="Incorrect Username or Password")

    return redirect("/")

def logoutView(request):
    return redirect("/accounts/logout")

def OTP(request, action):
    if not request.user.is_authenticated and not "verified" in request.session:
        if request.method == "GET":
            if action == "send" and "email" in request.GET and "name" in request.GET:
                print("block 1")
                email = request.GET["email"]
                if valid(email):
                    name = request.GET["name"]
                    otp = randint(100000, 999999)
                    text = render_to_string("email/otp.html",{"name":name,"otp":otp})
                    SendMailWithHtml(email, text,'one time password')
                    request.session["name"]= name
                    request.session["OTP"] = str(otp)
                    request.session["email"] = email
                    return register(request, success="OTP send", con={"email": email,"name":name})

            elif action == "verify" and "OTP" in request.GET and "OTP" in request.session:
                if request.session["OTP"] == request.GET["OTP"]:
                    request.session["verified"] = True
                    return register(request, success="OTP verified")

                elif "email" in request.session:
                    return register(request, error="INVALID OTP ! please try resending!", con={"email": request.session["email"]})

            return register(request, error="invalid information")

    return redirect("/")


def product(request,productID):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
    else:
        if "orderId" in request.session:
            try:
                order = Order.objects.get(pk=request.session["orderId"])
                print("order found")
            except:
                order = Order(complete=False)
                order.save()
                request.session["orderId"] = order.id
                print("couln't find order")
        else:
            order = Order(complete=False)
            order.save()
            request.session["orderId"] = order.id
            print("created new order")
            if "completed_orders" not in request.session:
                request.session["completed_orders"] = []
    try:
        prod = Product.objects.get(pk=productID)
    except:
        return store(request)
    return render(request,"store/product.html",{"product":prod,"order":order})