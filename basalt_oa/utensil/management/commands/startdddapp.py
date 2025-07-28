import os
from django.core.management.base import BaseCommand, CommandError

DDD_STRUCTURE = {
    "domain": ["entities.py", "services.py", "repositories.py"],
    "application": ["use_cases.py"],
    "infrastructure": ["orm_models.py", "repositories.py"],
    "interfaces": ["serializers.py", "views.py"]
}

class Command(BaseCommand):
    help = "创建符合 DDD 结构的 Django App"

    def add_arguments(self, parser):
        parser.add_argument("name", type=str, help="DDD App 名称")

    def handle(self, *args, **options):
        app_name = options["name"]
        base_path = os.path.join(os.getcwd(), app_name)

        if os.path.exists(base_path):
            raise CommandError(f"❌ 目录 {app_name} 已存在")

        os.makedirs(base_path)
        self.stdout.write(self.style.SUCCESS(f"📂 创建 DDD App: {app_name}"))

        # 生成 DDD 层级目录和文件
        for folder, files in DDD_STRUCTURE.items():
            folder_path = os.path.join(base_path, folder)
            os.makedirs(folder_path, exist_ok=True)
            open(os.path.join(folder_path, "__init__.py"), "w").close()
            for f in files:
                with open(os.path.join(folder_path, f), "w", encoding="utf-8") as fp:
                    fp.write(f"# {folder}/{f}\n")
            self.stdout.write(self.style.SUCCESS(f"  ✅ {folder} 已创建"))

        # tests 目录
        tests_path = os.path.join("tests")
        os.makedirs(tests_path, exist_ok=True)
        with open(os.path.join(tests_path, f"test_{app_name}.py"), "w", encoding="utf-8") as tf:
            tf.write(f"# tests/test_{app_name}.py\n")

        # app 根目录 __init__.py
        open(os.path.join(base_path, "__init__.py"), "w").close()

        self.stdout.write(self.style.SUCCESS("🎉 DDD App 目录创建成功！"))
