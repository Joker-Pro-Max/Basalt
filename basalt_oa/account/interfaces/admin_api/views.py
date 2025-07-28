from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from account.application.use_cases import RegisterUserUseCase, LoginUserUseCase, GetMyUserInfoUseCase, ListUsersUseCase
from account.infrastructure.repositories import DjangoUserRepository
from account.interfaces.admin_api.serializers import RegisterSerializer, LoginSerializer, UserListSerializer
from rest_framework import generics, permissions
from account.infrastructure.orm_models import User, System
from rest_framework_simplejwt.authentication import JWTAuthentication

from utensil.views import CustomPagination


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


# 获取用户信息
class MyUserInfoView(generics.RetrieveAPIView):
    authentication_classes = [JWTAuthentication]  # ✅ 需要JWT认证
    permission_classes = [permissions.IsAuthenticated]  # 只允许已登录用户

    def get(self, request, *args, **kwargs):
        try:
            # ✅ 从 request.user 获取 ID
            user_id = request.user.uuid or str(request.user.uuid)
            user_entity = GetMyUserInfoUseCase().execute(user_id)

            return Response({
                "uuid": user_entity.uuid,
                "username": user_entity.username,
                "email": user_entity.email,
                "phone": user_entity.phone,
                "system_code": user_entity.system_code,
                "roles": user_entity.roles,
                "permissions": user_entity.permissions
            })
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)


class UserListView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserListSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        filters = {
            "system": self.request.GET.get("system_code"),
            "username": self.request.GET.get("username"),
            "email": self.request.GET.get("email"),
            "phone": self.request.GET.get("phone"),
            "is_staff": self.request.GET.get("is_staff"),
            "is_active": self.request.GET.get("is_active"),
            "is_superuser": self.request.GET.get("is_superuser"),
            "role_id": self.request.GET.get("role_id"),
        }
        return ListUsersUseCase().execute(filters)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)  # ✅ 使用分页响应
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
