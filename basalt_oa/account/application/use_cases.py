from account.domain.services import UserDomainService
from account.infrastructure.repositories import DjangoUserRepository


class RegisterUserUseCase:
    def __init__(self):
        self.user_repo = DjangoUserRepository()

    def execute(self, username, email, phone, password, system_code):
        return UserDomainService(self.user_repo).register_user(username, email, phone, password, system_code)


class LoginUserUseCase:
    def __init__(self):
        self.user_repo = DjangoUserRepository()

    def execute(self, account, password, system_code):
        service = UserDomainService(self.user_repo)
        return service.authenticate_user(account, password, system_code)


class GetMyUserInfoUseCase:
    """用例：获取当前登录用户信息"""

    def __init__(self):
        self.user_repo = DjangoUserRepository()

    def execute(self, user_id: str):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")
        return user


class ListUsersUseCase:
    def __init__(self):
        self.user_repo = DjangoUserRepository()

    def execute(self, filters: dict):
        return UserDomainService(self.user_repo).list_users(filters)
