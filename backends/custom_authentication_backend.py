# from django.contrib.auth.backends import BaseBackend
# from django.contrib.auth import get_user_model

# class CustomEmailBackend(BaseBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         # Assuming the user model's username field is the email
#         UserModel = get_user_model()
#         try:
#             user = UserModel.objects.get(email=username)
#             if user.check_password(password):
#                 return user
#         except UserModel.DoesNotExist:
#             return None

#     def get_user(self, user_id):
#         UserModel = get_user_model()
#         try:
#             return UserModel.objects.get(pk=user_id)
#         except UserModel.DoesNotExist:
#             return None
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

class CustomEmailBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        print(f"[DEBUG] Trying to authenticate user: {username}")
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username)
            print("[DEBUG] User found:", user)
            if user.check_password(password):
                print("[DEBUG] Password correct")
                if user.is_active:
                    print("[DEBUG] User is active")
                    return user
                else:
                    print("[DEBUG] User is not active")
                    return None
            else:
                print("[DEBUG] Incorrect password")
                return None
        except UserModel.DoesNotExist:
            print("[DEBUG] No user found with email")
            return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
