# domain/entities.py
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class UserEntity:
    uuid: Optional[int]
    username: str
    email: Optional[str]
    phone: Optional[str]
    system_code: str
    roles: List[str]
    is_active: bool
    django_user: Optional[object] = None  # ✅ 允许保存 ORM User
    permissions: List[str] = None


@dataclass
class UserInfoEntity:
    uuid: Optional[str]
    username: str
    email: Optional[str]
    phone: Optional[str]
    system_code: str
    roles: List[str]
    django_user: Optional[object] = None  # ✅ 允许保存 ORM User
    permissions: List[str] = None
