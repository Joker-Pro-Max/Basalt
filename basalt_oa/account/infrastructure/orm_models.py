# infrastructure/orm_models.py
import logging
import re
from django.core.cache import cache
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Permission
from utensil.models import Base

logger = logging.getLogger('account')


# =====================
# 用户管理器
# =====================
class UserManager(BaseUserManager):
    def create_user(self, phone=None, email=None, password=None, **extra_fields):
        if not phone and not email:
            raise ValueError('必须提供手机号或邮箱')
        user = self.model(phone=phone, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone, email, password, **extra_fields)

    def get_by_account(self, account: str, system_code: str):
        cache_key = f'system:{system_code}'
        system = cache.get(cache_key)
        if system is None:
            try:
                system = System.objects.get(code=system_code)
                cache.set(cache_key, system, timeout=3600)
            except System.DoesNotExist:
                logger.warning(f"[Login] System not found: {system_code}")
                return None

        query = models.Q(system=system)
        if self._is_valid_email(account):
            query &= models.Q(email__iexact=account)
        elif self._is_valid_phone(account):
            query &= models.Q(phone=account)
        else:
            query &= models.Q(username=account)

        try:
            return self.get(query)
        except self.model.DoesNotExist:
            logger.info(f"[Login] User not found for {account} in system {system_code}")
            return None
        except self.model.MultipleObjectsReturned:
            logger.warning(f"[Login] Multiple users found for account={account}, system={system_code}")
            return self.filter(query).order_by('id').first()

    def _is_valid_email(self, account: str) -> bool:
        return bool(re.match(r"[^@]+@[^@]+\.[^@]+", account))

    def _is_valid_phone(self, account: str) -> bool:
        return bool(re.match(r"^1\d{10}$", account))


# =====================
# 用户模型
# =====================
class User(AbstractBaseUser, PermissionsMixin, Base):
    system = models.ForeignKey('System', on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    username = models.CharField(max_length=150, db_index=True, help_text="用户名")
    email = models.EmailField(unique=True, null=True, blank=True, help_text="唯一邮箱")
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True, help_text="唯一手机号")
    is_active = models.BooleanField(default=True, help_text="是否启用")
    is_staff = models.BooleanField(default=False, help_text="是否为后台管理员")
    is_superuser = models.BooleanField(default=False, help_text="是否为超级管理员")
    roles = models.ManyToManyField('Role', blank=True, related_name='users', help_text="所属角色")
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    class Meta:
        db_table = 'account_user'
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return self.username or self.email or self.phone or str(self.pk)

    @property
    def all_permissions(self):
        perms = set(self.user_permissions.values_list('codename', flat=True))
        for role in self.roles.all():
            perms.update(role.permissions.values_list('codename', flat=True))
        return list(perms)

    def has_perm(self, perm, obj=None):
        return perm in self.all_permissions or self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser or any(perm.startswith(app_label + ".") for perm in self.all_permissions)


# =====================
# 系统模型
# =====================
class System(Base):
    code = models.CharField(max_length=50, unique=True, help_text="系统唯一标识")
    name = models.CharField(max_length=100, help_text="系统名称")
    description = models.TextField(blank=True, null=True, help_text="系统说明")
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_systems',
        help_text="创建人"
    )

    class Meta:
        db_table = 'account_system'
        verbose_name = '系统'
        verbose_name_plural = '系统'

    def __str__(self):
        return self.name


# =====================
# 角色模型
# =====================
class Role(Base):
    system = models.ForeignKey("System", on_delete=models.CASCADE, related_name='roles')
    name = models.CharField(max_length=100, unique=True, help_text="角色名称")
    description = models.TextField(blank=True, null=True, help_text="角色描述")
    permissions = models.ManyToManyField(Permission, blank=True, related_name='custom_roles', help_text="角色权限")
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_roles',
        help_text="创建人"
    )

    class Meta:
        db_table = 'account_role'
        verbose_name = '角色'
        verbose_name_plural = '角色'

    def __str__(self):
        return self.name
