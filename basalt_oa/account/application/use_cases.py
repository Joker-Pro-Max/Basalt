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
