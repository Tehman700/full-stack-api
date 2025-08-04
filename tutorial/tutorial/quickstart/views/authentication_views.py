from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from quickstart.models.authentication_models import User_Data
from quickstart.models.signals_model import ActivityLog
from quickstart.serializers.user_data_serializer import User_Data_Serializer, LoginSerializer
from datetime import datetime

class LoginViewSet(viewsets.ViewSet):

    def dispatch(self, request, *args, **kwargs):
        if request.method != 'POST':
            return ResponseHandler.error(
                message=f"Method {request.method} not allowed. Only POST is supported.",
                code=1
            )
        return super().dispatch(request, *args, **kwargs)

    def create(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.validated_data

                now = datetime.now()
                pretty = now.strftime("%B %d, %Y at %I:%M %p")

                ActivityLog.objects.create(
                    user=user,
                    action='User logged in',
                    model_name='User',
                    instance_id=user.id,
                    description=f"{user.username} successfully logged in at {pretty}"
                )
                try:
                    user_profile = User_Data.objects.get(user=user)
                except User_Data.DoesNotExist:
                    return ResponseHandler.rest_error(
                        message="User profile not found",
                        errors="User profile does not exist"
                    )

                refresh = RefreshToken.for_user(user)
                user_data = {
                    "id": user.id,
                    "username": user.username,
                    "password" : request.data.get('password'),
                    "email": user.email or "Not provided",
                    "first_name": user.first_name or "Not provided",
                    "last_name": user.last_name or "Not provided",
                    "date_joined": user.date_joined,
                    "is_active": user.is_active,
                    "mobile_number": user_profile.mobile_number,
                    "role": user_profile.role,
                    "profile_created": user_profile.created
                }

                return ResponseHandler.rest_success({
                    "user": user_data,
                    "tokens": {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh)
                    }
                }, message="Login successful")

            return ResponseHandler.rest_error(
                message="Login failed",
                errors=serializer.errors
            )

        except Exception as e:
            return ResponseHandler.rest_error(
                message="Internal error occurred",
                errors=str(e),
                code=-1
            )

from quickstart.utils.response_handler import ResponseHandler


class RegisterAPIView(APIView):
    def post(self, request):
        try:
            required_fields = ['username', 'password', 'email', 'role', 'mobile_number', 'first_name', 'last_name']
            missing_fields = [field for field in required_fields if not request.data.get(field)]

            if missing_fields:
                return ResponseHandler.error(
                    message="Missing required fields",
                    errors={field: "This field is required." for field in missing_fields}
                )

            data = request.data
            username = data['username']
            password = data['password']
            email = data['email']
            role = data['role']
            mobile = data['mobile_number']
            first_name = data['first_name']
            last_name = data['last_name']

            if User.objects.filter(username=username).exists():
                return ResponseHandler.error("Username already exists")

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            profile = User_Data.objects.create(
                user=user,
                role=role,
                email_address=email,
                mobile_number=mobile,
                first_name=first_name,
                last_name=last_name,
            )

            profile_serializer = User_Data_Serializer(profile)

            return ResponseHandler.success(
                message="User successfully registered",
                data=profile_serializer.data
            )

        except Exception as e:
            return ResponseHandler.error(
                message="Something went wrong during registration",
                errors=str(e)
            )

    def http_method_not_allowed(self, request, *args, **kwargs):
        return ResponseHandler.error(
            message="Only POST is allowed on register",
            code=-1,
            errors=None
        )
