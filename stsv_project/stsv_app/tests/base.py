from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch

# Custom Test Runner đã đảm nhiệm việc seed data 1 lần duy nhất, nên không cần import seeders ở đây nữa.

User = get_user_model()

class BaseAPITestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.es_save_patcher = patch('django_elasticsearch_dsl.registries.registry.update')
        cls.es_delete_patcher = patch('django_elasticsearch_dsl.registries.registry.delete')
        cls.es_save_patcher.start()
        cls.es_delete_patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls.es_save_patcher.stop()
        cls.es_delete_patcher.stop()
        super().tearDownClass()

    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.filter(role=User.Role.STUDENT, is_active=True).first()
        cls.lecturer = User.objects.filter(role=User.Role.LECTURER, is_active=True).first()
        cls.org_officer = User.objects.filter(role=User.Role.ORGOFFICER, is_active=True).first()
        
        cls.admin = User.objects.filter(role=User.Role.ADMIN, is_active=True).first()
        if not cls.admin:
            cls.admin = User.objects.create_superuser(
                username='superadmin_test',
                password='123',
                email='admin@test.com',
                role=User.Role.ADMIN,
                is_active=True
            )
