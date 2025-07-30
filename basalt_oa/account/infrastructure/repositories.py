# infrastructure/repositories.py

from account.domain.entities import UserInfoEntity
from account.domain.repositories import IUserRepository
from account.infrastructure.orm_models import User, System


class DjangoUserRepository(IUserRepository):
    def get_by_account(self, account, system_code):
        return User.objects.get_by_account(account, system_code)

    def exists_by_email_or_phone(self, email, phone):  # noqa
        return User.objects.filter(email=email).exists() or User.objects.filter(phone=phone).exists()

    def get_by_id(self, user_id):  # noqa
        try:
            user = User.objects.get(pk=user_id)
            return UserInfoEntity(
                uuid=user.uuid,
                username=user.username,
                email=user.email,
                phone=user.phone,
                system_code=user.system.code if user.system else None,
                roles=[r.name for r in user.roles.all()],
                permissions=user.all_permissions
            )
        except User.DoesNotExist:
            return None

    def create(self, username, email, phone, password, system_code):  # noqa
        system, _ = System.objects.get_or_create(code=system_code, defaults={"name": "Basalt"})
        return User.objects.create_user(username=username, email=email, phone=phone, password=password, system=system)

    def filter_user(self, system=None, username=None, email=None, phone=None,  # noqa
                    is_staff=None, is_active=None, is_superuser=None, role_id=None):
        queryset = User.objects.filter(is_deleted=False).order_by('-created_at')
        if system:
            queryset = queryset.filter(system__uuid=system)
        if username:
            queryset = queryset.filter(username__contains=username)
        if email:
            queryset = queryset.filter(email__contains=email)
        if phone:
            queryset = queryset.filter(phone__contains=phone)
        if is_staff:
            queryset = queryset.filter(is_staff=is_staff)
        if is_active:
            queryset = queryset.filter(is_active=is_active)
        if is_superuser:
            queryset = queryset.filter(is_superuser=is_superuser)
        if role_id:
            queryset = queryset.filter(roles__id=role_id)
        return queryset
