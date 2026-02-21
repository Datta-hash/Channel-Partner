from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from .models import RegistrationRequest, AdminProfile, UserProfile, Subscription


# ---------------------------------------------------
# ✅ USER PROFILE TABLE (SEPARATE TABLE IN ADMIN)
# ---------------------------------------------------
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "phone",
        "country",
        "state",
        "city",
        "nature_of_business",
        "referral_code",
    )
    search_fields = ("user__username", "phone")
    list_filter = ("country", "state")


# ---------------------------------------------------
# ✅ REGISTRATION REQUEST
# ---------------------------------------------------
admin.site.register(RegistrationRequest)


# ---------------------------------------------------
# ✅ ADMIN PROFILE
# ---------------------------------------------------
@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone_number","email")


admin.site.register(Subscription)
