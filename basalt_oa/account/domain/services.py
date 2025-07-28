# domain/services.py
from account.domain.entities import UserEntity


class UserDomainService:
    def __init__(self, user_repo):
        self.user_repo = user_repo

    def register_user(self, username, email, phone, password, system_code):
        # 检查重复
        if self.user_repo.exists_by_email_or_phone(email, phone):
            raise ValueError("邮箱或手机号已注册")

        # 创建用户
        user = self.user_repo.create(username, email, phone, password, system_code)
        permissions = list(user.all_permissions)  # 调用 User 模型的 all_permissions 属性

        return UserEntity(
            uuid=user.uuid, username=user.username, email=user.email,
            phone=user.phone, system_code=system_code, roles=[], is_active=user.is_active,
            django_user=user, permissions=permissions
        )

    def authenticate_user(self, account, password, system_code):
        user = self.user_repo.get_by_account(account, system_code)
        if not user or not user.check_password(password):
            raise ValueError("账号或密码错误")
        if not user.is_active:
            raise ValueError("账户被禁用")
        return user


    def list_users(self, filters: dict):
        return self.user_repo.filter_user(**filters)