# infrastructure/repositories.py
from account.domain.entities import UserInfoEntity
from account.domain.repositories import IUserRepository
from account.infrastructure.orm_models import User, System


class DjangoUserRepository(IUserRepository):
    def get_by_account(self, account, system_code):
        return User.objects.get_by_account(account, system_code)

    def exists_by_email_or_phone(self, email, phone):
        return User.objects.filter(email=email).exists() or User.objects.filter(phone=phone).exists()

    def get_by_id(self, user_id):
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

    def create(self, username, email, phone, password, system_code):
        system, _ = System.objects.get_or_create(code=system_code, defaults={"name": "Basalt"})
        return User.objects.create_user(username=username, email=email, phone=phone, password=password, system=system)
