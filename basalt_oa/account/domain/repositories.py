# domain/repositories.py
from abc import ABC, abstractmethod

class IUserRepository(ABC):
    @abstractmethod
    def get_by_account(self, account: str, system_code: str): pass

    @abstractmethod
    def exists_by_email_or_phone(self, email: str, phone: str) -> bool: pass

    @abstractmethod
    def create(self, username: str, email: str, phone: str, password: str, system_code: str): pass
