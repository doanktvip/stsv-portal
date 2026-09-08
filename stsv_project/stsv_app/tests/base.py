from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
from stsv_app.models import StudentProfile, HomeroomClass

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
        if not cls.student:
            cls.student = User.objects.create_user(  # pragma: no cover
                username='student_test',  # pragma: no cover
                password='123',  # pragma: no cover
                email='student@test.com',  # pragma: no cover
                role=User.Role.STUDENT,  # pragma: no cover
                is_active=True  # pragma: no cover
            )  # pragma: no cover
            hc = HomeroomClass.objects.first()  # pragma: no cover
            StudentProfile.objects.create(  # pragma: no cover
                user=cls.student,
                student_id='TEST_SV_01',
                full_name='Test Student',
                faculty=hc.faculty if hc else None,
                homeroom_class=hc
            )
        elif not hasattr(cls.student, 'student_profile'): # pragma: no cover
            hc = HomeroomClass.objects.first()
            StudentProfile.objects.create(
                user=cls.student,
                student_id=f"SV_{cls.student.id}",
                full_name=cls.student.get_full_name() or cls.student.username,
                faculty=hc.faculty if hc else None,
                homeroom_class=hc
            )

        cls.bancansu = User.objects.filter(role=User.Role.BANCANSU, is_active=True).first()
        cls.org_officer = User.objects.filter(role=User.Role.ORGOFFICER, is_active=True).first()
        
        cls.admin = User.objects.filter(role=User.Role.ADMIN, is_active=True).first()
        if not cls.admin: # pragma: no cover
            cls.admin = User.objects.create_superuser(
                username='superadmin_test',
                password='123',
                email='admin@test.com',
                role=User.Role.ADMIN,
                is_active=True
            )
