# b_system/interfaces/authentication.py
import jwt
from rest_framework import authentication, exceptions
from django.conf import settings

class RemoteJWTAuthentication(authentication.BaseAuthentication):
    """
    只解析 JWT，不依赖 B 系统 User 模型。
    """
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None  # 无 token 继续其他认证类

        token = auth_header.split(' ')[1]
        try:
            # ✅ 解析 JWT
            payload = jwt.decode(token, settings.SIMPLE_JWT['SIGNING_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token 已过期')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('无效的 Token')

        # ✅ 只返回 payload，不查 ORM
        user_info = {
            "uuid": payload.get("user_id"),    # A 系统 JWT 中的 user_id 是 uuid
            "username": payload.get("username"),
            "email": payload.get("email"),
            "permissions": payload.get("permissions", [])
        }

        # ✅ 在 B 系统中 request.user 仍需一个对象，可使用 SimpleLazyObject
        return (SimpleRemoteUser(user_info), None)


class SimpleRemoteUser:
    """ 轻量用户对象，不依赖 ORM """
    def __init__(self, info):
        self.uuid = info.get("uuid")
        self.username = info.get("username")
        self.email = info.get("email")
        self.permissions = info.get("permissions", [])

    @property
    def is_authenticated(self):
        return True
