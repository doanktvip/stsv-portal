from django.test import TestCase
from unittest.mock import patch, MagicMock
from stsv_app.services.push_notification import PushNotificationService
from django.contrib.auth import get_user_model

User = get_user_model()

class PushNotificationServiceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="push_user")

    @patch('firebase_admin.messaging.send_each_for_multicast')
    @patch('firebase_admin._apps', {'[DEFAULT]': 'app'})
    def test_send_push_notification_success(self, mock_send):
        mock_user = MagicMock()
        mock_devices = MagicMock()
        mock_devices.exclude.return_value.exclude.return_value.exists.return_value = True
        mock_devices.exclude.return_value.exclude.return_value.values_list.return_value = ["token123"]
        mock_user.devices = mock_devices

        # Mock the response
        mock_response = MagicMock()
        mock_response.success_count = 1
        mock_send.return_value = mock_response

        result = PushNotificationService.send_push_notification(
            user=mock_user,
            title="Hello",
            body="World"
        )
        self.assertTrue(result)
        mock_send.assert_called_once()

    @patch('firebase_admin._apps', {})
    def test_send_push_notification_no_firebase(self):
        result = PushNotificationService.send_push_notification(
            user=self.user,
            title="Hello",
            body="World"
        )
        self.assertFalse(result)

    @patch('firebase_admin._apps', {'[DEFAULT]': 'app'})
    def test_send_push_notification_no_devices(self):
        # Mock devices empty
        mock_user = MagicMock()
        mock_devices = MagicMock()
        mock_devices.exclude.return_value.exclude.return_value.exists.return_value = False
        mock_user.devices = mock_devices
        
        result = PushNotificationService.send_push_notification(
            user=mock_user,
            title="Hello",
            body="World"
        )
        self.assertFalse(result)

    @patch('firebase_admin.messaging.send_each_for_multicast')
    @patch('firebase_admin._apps', {'[DEFAULT]': 'app'})
    def test_send_push_notification_exception(self, mock_send):
        mock_send.side_effect = Exception("Firebase error")
        
        mock_user = MagicMock()
        mock_devices = MagicMock()
        mock_devices.exclude.return_value.exclude.return_value.exists.return_value = True
        mock_devices.exclude.return_value.exclude.return_value.values_list.return_value = ["token123"]
        mock_user.devices = mock_devices
        
        result = PushNotificationService.send_push_notification(
            user=mock_user,
            title="Hello",
            body="World"
        )
        self.assertFalse(result)

    @patch('stsv_app.services.push_notification.PushNotificationService.send_push_notification')
    def test_send_to_multiple_users(self, mock_send):
        user2 = User.objects.create(username="push_user2")
        PushNotificationService.send_to_multiple_users(
            users=[self.user, user2],
            title="Title",
            body="Body"
        )
        self.assertEqual(mock_send.call_count, 2)
