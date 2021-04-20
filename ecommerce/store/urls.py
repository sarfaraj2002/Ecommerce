from django.urls import path
from . import views




urlpatterns=[

    path("",views.store,name="store"),
    path("cart/",views.cart,name="cart"),
    path("checkout/",views.checkout,name="checkout"),
    path("update_item/",views.updateItem,name="update_items"),
    path("order/submit/",views.submitorder,name="submitorder"),

    path("register/",views.register,name="register"),
    path("otp/<str:action>/",views.OTP,name = "OTP"),
    path("login/",views.loginView,name="loginView"),
    path("logout/",views.logoutView,name="logoutView"),
    path("product/<str:productID>/",views.product,name="product")

]

