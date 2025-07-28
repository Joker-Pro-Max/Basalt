from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from account.application.use_cases import RegisterUserUseCase, LoginUserUseCase
from account.interfaces.admin_api.serializers import RegisterSerializer, LoginSerializer
from rest_framework import generics, permissions
from account.infrastructure.orm_models import User, System


class RegisterView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        system_code = request.headers.get("X-System-Code", "default")

        try:
            # 执行注册用例
            user_entity = RegisterUserUseCase().execute(
                username=data['username'],
                email=data.get('email'),
                phone=data.get('phone'),
                password=data['password'],
                system_code=system_code
            )

            # 生成 JWT token
            refresh = RefreshToken.for_user(user_entity.django_user)

            return Response({
                "msg": "注册成功",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "uuid": user_entity.uuid,
                    "username": user_entity.username,
                    "email": user_entity.email,
                    "phone": user_entity.phone,
                    "system": user_entity.system_code,
                    "permissions": user_entity.permissions
                }
            }, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        system_code = request.headers.get("X-System-Code", "Basalt")
        try:
            user = LoginUserUseCase().execute(data['account'], data['password'], system_code)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "uuid": user.uuid,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "system": user.system.code if user.system else None,
                "permissions": user.all_permissions
            }
        })


class InitSuperAdminView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = None

    def post(self, request, *args, **kwargs):  # noqa
        email = request.data.get("email")
        phone = request.data.get("phone")
        if User.objects.filter(is_superuser=True).exists():
            return Response({"detail": "超级管理员已存在"}, status=status.HTTP_400_BAD_REQUEST)

        system, _ = System.objects.get_or_create(code="default", defaults={"name": "默认系统"})
        user = User.objects.create_user(
            username="admin", email=email, phone=phone,
            password="admin123456", system=system,
            is_superuser=True, is_staff=True
        )
        return Response({"msg": "超级管理员创建成功", "user": {"uuid": user.uuid, "email": user.email}},
                        status=status.HTTP_201_CREATED)
