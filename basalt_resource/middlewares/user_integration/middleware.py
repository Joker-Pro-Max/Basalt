import requests
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache

A_SYSTEM_ME_API = f"{settings.ACCOUNT_API_HOST}/api/account/me/"


class RemoteJWTMiddleware(MiddlewareMixin):
    """提取 JWT 并缓存用户信息（供 DRF 认证类使用）"""

    def process_request(self, request):  # noqa
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            request.jwt_token = None
            request.jwt_user_data = None
            return

        token = auth_header.split(" ")[1]
        request.jwt_token = token

        # 优先从缓存获取用户数据
        cache_key = f"user_jwt:{token}"
        user_data = cache.get(cache_key)
        if not user_data:
            try:
                res = requests.get(A_SYSTEM_ME_API, headers={"Authorization": f"Bearer {token}"}, timeout=5)
                if res.status_code == 200:
                    user_data = res.json()
                    cache.set(cache_key, user_data, timeout=300)
                else:
                    user_data = None
            except Exception as e:
                user_data = None

        request.jwt_user_data = user_data
