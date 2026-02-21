from django.urls import path
from .views import RegisterView, SendOTPView, VerifyOTPView, UserListView, ApproveRegistrationView
from . views import ValidateReferralCodeView, VerifyEmailOTPView, CreateSubscriptionView, GetSubscriptionView, GetCommissionView



urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-email-otp/", VerifyEmailOTPView.as_view(), name='verify-email-otp'),
    path("send-otp/", SendOTPView.as_view(), name="send-otp"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("getuserlist/", UserListView.as_view(), name="user-list"),
    path("approve-registration/<int:pk>/", ApproveRegistrationView.as_view(), name="approve-registration"),
    path('validate-referral/', ValidateReferralCodeView.as_view(), name='validate-referral'),
    path('subscription/create/', CreateSubscriptionView.as_view(), name='create-subscription'),
    path('subscription/list/', GetSubscriptionView.as_view(), name='list-subscription'),
    path('commission/list/', GetCommissionView.as_view(), name='list-commission'),
    

]
