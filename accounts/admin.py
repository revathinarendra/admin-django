from django.contrib import admin
from .models import UserProfile, EmailVerificationToken
from django.contrib.auth.models import User
from django.utils.html import format_html

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'get_full_name',
        'phone_number',
        'gender',
        'city',
        'state',
        'country',
        'profile_pic_preview',
    )
    search_fields = ('user__username', 'user__email', 'phone_number', 'city', 'state')
    list_filter = ('gender', 'city', 'state', 'country')

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Full Name'

    def profile_pic_preview(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.profile_picture.url)
        return "-"
    profile_pic_preview.short_description = 'Profile Picture'


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'is_expired')
    readonly_fields = ('token', 'created_at')
    search_fields = ('user__username', 'user__email')

    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
