import random
import string
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from twilio.base.exceptions import TwilioRestException
from services.permissions import IsAdminProfile
from services.twilio_verify_service import send_otp, verify_otp
from .models import RegistrationRequest, UserProfile, AdminProfile, Subscription, Commission
from .serializers import RegistrationRequestSerializer

User = get_user_model()


# -----------------------------------------------
# ✅ REGISTER
# -----------------------------------------------


from rest_framework.response import Response
from rest_framework import status
import uuid

User = get_user_model()


# class RegisterView(CreateAPIView):
#     queryset = RegistrationRequest.objects.all()
#     serializer_class = RegistrationRequestSerializer
#     permission_classes = [AllowAny]

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         try:
#             self.perform_create(serializer)
#         except Exception as e:
#             if serializer.instance:
#                 serializer.instance.delete()
#             return Response(
#                 {
#                     "status": 500,
#                     "success": False,
#                     "message": "Registration failed. Unable to send email. Please try again.",
#                     "data": None,
#                     "traceId": str(uuid.uuid4()),
#                 },
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

#         instance = serializer.instance

#         return Response(
#             {
#                 "status": 201,
#                 "success": True,
#                 "message": "Registration Successful",
                
#                 "user": {
#                         "name": instance.name,
#                         "email": instance.email,
#                         "phone": f"{instance.country_code}{instance.phone}",
#                         "country": instance.country.country_name,
#                         "state": instance.state.state_name,
#                         "city": instance.city.city_name,
#                         "nature_of_business": instance.nature_of_business.nature_of_business,
#                         "approval_status": instance.approval_status,
                    
#                                 },
#                 "traceId": str(uuid.uuid4()),
#             },
#             status=status.HTTP_201_CREATED,
#         )

#     def perform_create(self, serializer):
#         validated_data = serializer.validated_data
#         name = validated_data.get('name')
#         email = validated_data.get('email')
#         phone = validated_data.get('phone')

#         admin_emails = list(AdminProfile.objects.filter(
#             email__isnull=False
#         ).values_list('email', flat=True))

#         send_mail(
#             subject="Registration Request Received",
#             message=f"Dear {name},\n\nThank you for registering. Your request has been received and is currently under review.\n\nWe will notify you once your request has been processed.\n\nThank you!",
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[email],
#             fail_silently=False,
#         )

#         if admin_emails:
#             send_mail(
#                 subject="New Registration Request",
#                 message=f"A new registration request has been received.\n\nDetails:\nName: {name}\nEmail: {email}\nPhone: {phone}\n\nPlease review and approve or reject the request.",
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=admin_emails,
#                 fail_silently=False,
#             )

#         serializer.save()


from django.core.cache import cache


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "status": 400,
                    "success": False,
                    "message": "Registration failed.",
                    "data": serializer.errors,
                    "traceId": str(uuid.uuid4()),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data['email']

        # Generate 6 digit OTP
        otp = str(random.randint(100000, 999999))

        # Store OTP and registration data in Redis for 10 minutes
        cache.set(f"email_otp_{email}", otp, timeout=600)
        cache.set(f"registration_data_{email}", {
            "name": serializer.validated_data['name'],
            "email": email,
            "country_code": serializer.validated_data['country_code'],
            "phone": serializer.validated_data['phone'],
            "country_id": serializer.validated_data['country'].id,
            "state_id": serializer.validated_data['state'].id,
            "city_id": serializer.validated_data['city'].id,
            "nature_of_business_id": serializer.validated_data['nature_of_business'].id,
        }, timeout=600)

        # Send OTP via SMTP
        try:
            send_mail(
                subject="Email Verification OTP",
                message=f"Dear {serializer.validated_data['name']},\n\nYour OTP for email verification is:\n\n{otp}\n\nThis OTP is valid for 10 minutes.\n\nDo not share this OTP with anyone.\n\nThank you!",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception:
            cache.delete(f"email_otp_{email}")
            cache.delete(f"registration_data_{email}")
            return Response(
                {
                    "status": 500,
                    "success": False,
                    "message": "Registration failed. Unable to send OTP email. Please try again.",
                    "data": None,
                    "traceId": str(uuid.uuid4()),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "status": 200,
                "success": True,
                "message": "OTP sent successfully. Please verify your email.",
                "data": {
                    "email": email,
                },
                "traceId": str(uuid.uuid4()),
            },
            status=status.HTTP_200_OK,
        )
    

class VerifyEmailOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        if not email or not otp:
            return Response(
                {
                    "status": 400,
                    "success": False,
                    "message": "Email and OTP are required.",
                    "data": None,
                    "traceId": str(uuid.uuid4()),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get OTP from Redis
        cached_otp = cache.get(f"email_otp_{email}")

        # Check if OTP expired
        if not cached_otp:
            cache.delete(f"registration_data_{email}")
            return Response(
                {
                    "status": 400,
                    "success": False,
                    "message": "OTP has expired. Please register again.",
                    "data": None,
                    "traceId": str(uuid.uuid4()),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check OTP match
        if cached_otp != otp:
            return Response(
                {
                    "status": 400,
                    "success": False,
                    "message": "Invalid OTP. Please try again.",
                    "data": None,
                    "traceId": str(uuid.uuid4()),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get registration data from Redis
        registration_data = cache.get(f"registration_data_{email}")

        if not registration_data:
            return Response(
                {
                    "status": 400,
                    "success": False,
                    "message": "Registration data expired. Please register again.",
                    "data": None,
                    "traceId": str(uuid.uuid4()),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Save to DB only after OTP verification
        instance = RegistrationRequest.objects.create(
            name=registration_data['name'],
            email=registration_data['email'],
            country_code=registration_data['country_code'],
            phone=registration_data['phone'],
            country_id=registration_data['country_id'],
            state_id=registration_data['state_id'],
            city_id=registration_data['city_id'],
            nature_of_business_id=registration_data['nature_of_business_id'],
            is_email_verified=True,
        )

        # Clear Redis cache
        cache.delete(f"email_otp_{email}")
        cache.delete(f"registration_data_{email}")

        # Send confirmation email to client
        try:
            send_mail(
                subject="Registration Successful",
                message=f"Dear {instance.name},\n\nYour registration has been received successfully.\n\nYour registration is currently under review. We will notify you once your request has been processed.\n\nDetails:\nName: {instance.name}\nEmail: {instance.email}\nPhone: {instance.country_code}{instance.phone}\n\nThank you!",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                fail_silently=False,
            )

            # Send notification email to admins
            admin_emails = list(AdminProfile.objects.filter(
                email__isnull=False
            ).values_list('email', flat=True))

            if admin_emails:
                send_mail(
                    subject="New Registration Request",
                    message=f"A new registration request has been received.\n\nDetails:\nName: {instance.name}\nEmail: {instance.email}\nPhone: {instance.country_code}{instance.phone}\n\nPlease review and approve or reject the request.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=admin_emails,
                    fail_silently=False,
                )

        except Exception:
            return Response(
                {
                    "status": 500,
                    "success": False,
                    "message": "Registration saved but confirmation email could not be sent.",
                    "data": None,
                    "traceId": str(uuid.uuid4()),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "status": 201,
                "success": True,
                "message": "Email verified successfully. Your registration is under review.",
                "data": {
                    "name": instance.name,
                    "email": instance.email,
                    "phone": f"{instance.country_code}{instance.phone}",
                    "country": instance.country.country_name,
                    "state": instance.state.state_name,
                    "city": instance.city.city_name,
                    "nature_of_business": instance.nature_of_business.nature_of_business,
                    "approval_status": instance.approval_status,
                },
                "traceId": str(uuid.uuid4()),
            },
            status=status.HTTP_201_CREATED,
        )

# -----------------------------------------------
# ✅ SEND OTP
# -----------------------------------------------
class SendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        country_code = request.data.get("country_code")
        phone = request.data.get("phone")

        if not phone:
            return Response(
                {"error": "Phone number is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not country_code:
            return Response(
                {"error": "Country code is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        full_phone = f"{country_code}{phone}"

        # check if phone exists in UserProfile or AdminProfile
        is_user = UserProfile.objects.filter(phone=phone).exists()
        is_admin = AdminProfile.objects.filter(phone_number=phone).exists()

        if not is_user and not is_admin:
            return Response(
                {"error": "Phone number not registered."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            send_otp(full_phone)
        except TwilioRestException as e:
            if e.code == 21608:
                return Response(
                    {"error": "This phone number is not verified. Please contact support."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {"error": "Failed to send OTP. Please try again."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"message": "OTP sent successfully."},
            status=status.HTTP_200_OK
        )


# -----------------------------------------------
# ✅ VERIFY OTP
# -----------------------------------------------
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        country_code = request.data.get("country_code")
        phone = request.data.get("phone")
        otp = request.data.get("otp")

        if not phone or not otp:
            return Response(
                {
                    "status": 400,
                    "success": False,
                    "message": "Phone and OTP are required.",
                    "data": None,
                    "traceId": str(uuid.uuid4()),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not country_code:
            return Response(
                {
                    "status": 400,
                    "success": False,
                    "message": "Country code is required.",
                    "data": None,
                    "traceId": str(uuid.uuid4()),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        full_phone = f"{country_code}{phone}"

        # verify otp via twilio
        otp_status = verify_otp(full_phone, otp)

        if otp_status != "approved":
            return Response(
                {
                    "status": 400,
                    "success": False,
                    "message": "Invalid or expired OTP.",
                    "data": None,
                    "traceId": str(uuid.uuid4()),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # identify user type
        try:
            user_profile = UserProfile.objects.get(phone=phone)
            user = user_profile.user
            role = "user"
        except UserProfile.DoesNotExist:
            try:
                admin_profile = AdminProfile.objects.get(phone_number=phone)
                user = admin_profile.user
                role = "admin"
            except AdminProfile.DoesNotExist:
                return Response(
                    {
                        "status": 404,
                        "success": False,
                        "message": "No account found with this phone number.",
                        "data": None,
                        "traceId": str(uuid.uuid4()),
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

        # generate JWT token
        refresh = RefreshToken.for_user(user)

        data = {
            "accessToken": str(refresh.access_token),
            "refreshToken": str(refresh),
        }

        if role == "admin":
            data["user"] = {
                "phone": admin_profile.phone_number,
            }

        if role == "user":
            data["user"] = {
                "phone": user_profile.phone,
                "email": user_profile.email,
                "country": user_profile.country.country_name,
                "state": user_profile.state.state_name,
                "city": user_profile.city.city_name,
                "nature_of_business": user_profile.nature_of_business.nature_of_business,
                "referral_code": user_profile.referral_code,
            }

        return Response(
            {
                "status": 200,
                "success": True,
                "message": "OTP verified successfully.",
                "data": data,
                "traceId": str(uuid.uuid4()),
            },
            status=status.HTTP_200_OK,
        )


# -----------------------------------------------
# ✅ USER LIST (ADMIN ONLY)
# -----------------------------------------------
class UserListView(ListAPIView):
    serializer_class = RegistrationRequestSerializer
    permission_classes = [IsAdminProfile]

    def get_queryset(self):
        return RegistrationRequest.objects.all()


# -----------------------------------------------
# ✅ APPROVE / REJECT REGISTRATION
# -----------------------------------------------
def generate_referral_code():
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not UserProfile.objects.filter(referral_code=code).exists():
            return code


class ApproveRegistrationView(APIView):
    permission_classes = [IsAdminProfile]

    def patch(self, request, pk):
        try:
            instance = RegistrationRequest.objects.get(pk=pk)
        except RegistrationRequest.DoesNotExist:
            return Response(
                {"error": "Registration request not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        new_status = request.data.get("approval_status")

        if new_status not in ["APPROVED", "REJECTED"]:
            return Response(
                {"error": "Invalid status. Must be APPROVED or REJECTED."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_status == "APPROVED":

            # avoid duplicate user creation
            if User.objects.filter(email=instance.email).exists():
                return Response(
                    {"error": "User already exists."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # check if email already exists in UserProfile
            if UserProfile.objects.filter(email=instance.email).exists():
                return Response(
                    {"error": "Email already exists in User Profile."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # check if phone already exists in UserProfile or AdminProfile
            if UserProfile.objects.filter(phone=instance.phone).exists():
                return Response(
                    {"error": "Phone number already exists in User Profile."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if AdminProfile.objects.filter(phone_number=instance.phone).exists():
                return Response(
                    {"error": "Phone number already exists in Admin Profile."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # create Django user
            user = User.objects.create_user(
                username=instance.email,
                email=instance.email,
                first_name=instance.name,
                password=None
            )

            # generate referral code
            referral_code = generate_referral_code()

            # create user profile
            UserProfile.objects.create(
                user=user,
                email=instance.email,
                phone=instance.phone,
                country=instance.country,
                state=instance.state,
                city=instance.city,
                nature_of_business=instance.nature_of_business,
                referral_code=referral_code,
            )

            # send approval email
            send_mail(
                subject="Registration Approved",
                message=f"Dear {instance.name},\n\nCongratulations! Your registration has been approved.\n\nYour referral code is: {referral_code}\n\nWelcome aboard!",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                fail_silently=False,
            )

            # delete from registration table
            instance.delete()

            return Response(
                {"message": "User approved and registered successfully."},
                status=status.HTTP_200_OK
            )

        if new_status == "REJECTED":
            email = instance.email
            name = instance.name

            # delete from registration table
            instance.delete()

            # send rejection email
            send_mail(
                subject="Registration Rejected",
                message=f"Dear {name},\n\nWe regret to inform you that your registration request has been rejected.\n\nPlease contact support for more information.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            return Response(
                {"message": "Registration rejected and user notified via email."},
                status=status.HTTP_200_OK
            )


    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from services.permissions import IsValidAPIKey
from User.models.user_profile import UserProfile
import uuid



class ValidateReferralCodeView(APIView):
    permission_classes = [IsValidAPIKey]  # <-- changed from AllowAny

    def post(self, request):
        referral_code = request.data.get("referral_code")

        if not referral_code:
            return Response(
                {
                    "status": 400,
                    "success": False,
                    "message": "Referral code is required.",
                    "data": None,
                    "traceId": str(uuid.uuid4()),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        exists = UserProfile.objects.filter(referral_code=referral_code).exists()

        if exists:
            return Response(
                {
                    "status": 200,
                    "success": True,
                    "message": "Valid Referral Code.",
                    "data": {
                        "referral_code": referral_code,
                        "is_valid": True,
                    },
                    "traceId": str(uuid.uuid4()),
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "status": 200,
                "success": False,
                "message": "Invalid Referral Code.",
                "data": {
                    "referral_code": referral_code,
                    "is_valid": False,
                },
                "traceId": str(uuid.uuid4()),
            },
            status=status.HTTP_200_OK,
        )
    
import requests
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
from .models import Subscription
from Meta.models.meta_nature_of_business import NatureOfBusiness


class CreateSubscriptionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        company_name = request.data.get("company_name")

        if not company_name:
            return Response(
                {
                    "status": 400,
                    "success": False,
                    "message": "company_name is required.",
                    "data": None,
                    "traceId": str(uuid.uuid4()),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Fetch registration details from Project B
        try:
            response = requests.get(
                "http://127.0.0.1:8001/api/registration/fetch/",
                params={"company_name": company_name},
                headers={
                    "X-API-KEY": settings.INTER_SERVICE_API_KEY,
                    "Content-Type": "application/json",
                },
                timeout=5
            )
            reg_data = response.json()

            if not reg_data.get("success"):
                return Response(
                    {
                        "status": 404,
                        "success": False,
                        "message": "Registration not found.",
                        "data": None,
                        "traceId": str(uuid.uuid4()),
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

        except requests.exceptions.ConnectionError:
            return Response(
                {
                    "status": 503,
                    "success": False,
                    "message": "Unable to connect to the registration service.",
                    "data": None,
                    "traceId": str(uuid.uuid4()),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except requests.exceptions.Timeout:
            return Response(
                {
                    "status": 504,
                    "success": False,
                    "message": "Registration service request timed out.",
                    "data": None,
                    "traceId": str(uuid.uuid4()),
                },
                status=status.HTTP_504_GATEWAY_TIMEOUT,
            )

        # Get registration data
        item = reg_data['data']

        # Get or create NatureOfBusiness
        nature_of_business, _ = NatureOfBusiness.objects.get_or_create(
            nature_of_business=item['nature_of_business']
        )

        # Check if subscription already exists
        if Subscription.objects.filter(company_email=item['company_email']).exists():
            return Response(
                {
                    "status": 400,
                    "success": False,
                    "message": "Subscription already exists for this company.",
                    "data": None,
                    "traceId": str(uuid.uuid4()),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Save to Subscription table
        subscription = Subscription.objects.create(
            company_name=item['company_name'],
            company_email=item['company_email'],
            number=item['mobile_number'],
            contact_person=item['contact_person'],
            nature_of_business=nature_of_business,
            subscription_type=item['subscription_type'],
            employee_count=item['number_of_employees'],
            total_paid_amount=item['total_paid_amount'],
            referral_code=item['referred_by'],
            start_date=item['start_date'],
            end_date=item['end_date'],
            payment_status=item['payment_status'],
            demo_status=item['demo_status'],
            user=request.user,
        )

        return Response(
            {
                "status": 201,
                "success": True,
                "message": "Subscription created successfully.",
                "data": {
                    "id": str(subscription.id),
                    "company_name": subscription.company_name,
                    "company_email": subscription.company_email,
                    "number": subscription.number,
                    "contact_person": subscription.contact_person,
                    "nature_of_business": subscription.nature_of_business.nature_of_business,
                    "subscription_type": subscription.subscription_type,
                    "employee_count": subscription.employee_count,
                    "total_paid_amount": str(subscription.total_paid_amount),
                    "referral_code": subscription.referral_code,
                    "start_date": str(subscription.start_date),
                    "end_date": str(subscription.end_date),
                    "payment_status": subscription.payment_status,
                    "demo_status": subscription.demo_status,
                },
                "traceId": str(uuid.uuid4()),
            },
            status=status.HTTP_201_CREATED,
        )


import requests
import uuid
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
from .models import Subscription, Commission
from Meta.models.meta_nature_of_business import NatureOfBusiness


class CreateSubscriptionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        company_name = request.data.get("company_name")

        if not company_name:
            return Response(
                {
                    "status": 400,
                    "success": False,
                    "message": "company_name is required.",
                    "data": None,
                    "traceId": str(uuid.uuid4()),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Fetch registration details from Project B
        try:
            response = requests.get(
                "http://127.0.0.1:8001/api/registration/fetch/",
                params={"company_name": company_name},
                headers={
                    "X-API-KEY": settings.INTER_SERVICE_API_KEY,
                    "Content-Type": "application/json",
                },
                timeout=5
            )
            reg_data = response.json()

            if not reg_data.get("success"):
                return Response(
                    {
                        "status": 404,
                        "success": False,
                        "message": "Registration not found.",
                        "data": None,
                        "traceId": str(uuid.uuid4()),
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

        except requests.exceptions.ConnectionError:
            return Response(
                {
                    "status": 503,
                    "success": False,
                    "message": "Unable to connect to the registration service.",
                    "data": None,
                    "traceId": str(uuid.uuid4()),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except requests.exceptions.Timeout:
            return Response(
                {
                    "status": 504,
                    "success": False,
                    "message": "Registration service request timed out.",
                    "data": None,
                    "traceId": str(uuid.uuid4()),
                },
                status=status.HTTP_504_GATEWAY_TIMEOUT,
            )

        # Get registration data
        item = reg_data['data']

        # Check if subscription already exists
        if Subscription.objects.filter(company_email=item['company_email']).exists():
            return Response(
                {
                    "status": 400,
                    "success": False,
                    "message": "Subscription already exists for this company.",
                    "data": None,
                    "traceId": str(uuid.uuid4()),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get or create NatureOfBusiness
        nature_of_business, _ = NatureOfBusiness.objects.get_or_create(
            nature_of_business=item['nature_of_business']
        )

        # Save to Subscription table
        subscription = Subscription.objects.create(
            company_name=item['company_name'],
            company_email=item['company_email'],
            number=item['mobile_number'],
            contact_person=item['contact_person'],
            nature_of_business=nature_of_business,
            subscription_type=item['subscription_type'],
            employee_count=item['number_of_employees'],
            total_paid_amount=item['total_paid_amount'],
            referral_code=item['referred_by'],
            start_date=item['start_date'],
            end_date=item['end_date'],
            payment_status=item['payment_status'],
            demo_status=item['demo_status'],
            user=request.user,
        )

        # Auto-create commission if referred_by exists
        commission_data = None
        if item['referred_by']:
            try:
                user_profile = UserProfile.objects.get(referral_code=item['referred_by'])
                commission_user = user_profile.user
            except UserProfile.DoesNotExist:
                commission_user = None

            commission_percentage = Decimal('10.00')
            total_paid_amount = Decimal(str(item['total_paid_amount']))
            commission_amount = (total_paid_amount * commission_percentage) / 100

            commission = Commission.objects.create(
                subscription=subscription,
                user=commission_user,
                referred_by=item['referred_by'],
                commission_percentage=commission_percentage,
                commission_amount=commission_amount,
                status='PENDING',
            )
            commission_data = {
                "referred_by": commission.referred_by,
                "user": commission_user.username if commission_user else None,
                "commission_percentage": str(commission.commission_percentage),
                "commission_amount": str(commission.commission_amount),
                "status": commission.status,
            }

        return Response(
            {
                "status": 201,
                "success": True,
                "message": "Subscription created successfully.",
                "data": {
                    "id": str(subscription.id),
                    "company_name": subscription.company_name,
                    "company_email": subscription.company_email,
                    "number": subscription.number,
                    "contact_person": subscription.contact_person,
                    "nature_of_business": subscription.nature_of_business.nature_of_business,
                    "subscription_type": subscription.subscription_type,
                    "employee_count": subscription.employee_count,
                    "total_paid_amount": str(subscription.total_paid_amount),
                    "referral_code": subscription.referral_code,
                    "start_date": str(subscription.start_date),
                    "end_date": str(subscription.end_date),
                    "payment_status": subscription.payment_status,
                    "demo_status": subscription.demo_status,
                    "commission": commission_data,
                },
                "traceId": str(uuid.uuid4()),
            },
            status=status.HTTP_201_CREATED,
        )


class GetSubscriptionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subscriptions = Subscription.objects.select_related(
            'nature_of_business',
            'user'
        ).all()

        data = []
        for sub in subscriptions:
            data.append({
                "id": str(sub.id),
                "company_name": sub.company_name,
                "company_email": sub.company_email,
                "number": sub.number,
                "contact_person": sub.contact_person,
                "nature_of_business": sub.nature_of_business.nature_of_business,
                "subscription_type": sub.subscription_type,
                "employee_count": sub.employee_count,
                "total_paid_amount": str(sub.total_paid_amount),
                "referral_code": sub.referral_code,
                "start_date": str(sub.start_date),
                "end_date": str(sub.end_date),
                "payment_status": sub.payment_status,
                "demo_status": sub.demo_status,
            })

        return Response(
            {
                "status": 200,
                "success": True,
                "message": "Subscriptions fetched successfully.",
                "data": {
                    "items": data,
                    "total": len(data),
                },
                "traceId": str(uuid.uuid4()),
            },
            status=status.HTTP_200_OK,
        )


class GetCommissionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Admin sees all commissions
        if hasattr(request.user, 'adminprofile'):
            commissions = Commission.objects.select_related('subscription', 'user').all()
        else:
            # User sees only their own commissions
            commissions = Commission.objects.select_related('subscription', 'user').filter(user=request.user)
        
        data = []
        for com in commissions:
            data.append({
                "id": str(com.id),
                "subscription": com.subscription.company_name,
                "referred_by": com.referred_by,
                "user": com.user.username if com.user else None,
                "commission_percentage": str(com.commission_percentage),
                "commission_amount": str(com.commission_amount),
                "status": com.status,
                "created_at": str(com.created_at),
            })

        return Response(
            {
                "status": 200,
                "success": True,
                "message": "Commissions fetched successfully.",
                "data": {
                    "items": data,
                    "total": len(data),
                },
                "traceId": str(uuid.uuid4()),
            },
            status=status.HTTP_200_OK,
        )