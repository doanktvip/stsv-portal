from django.urls import reverse
from rest_framework import status
from unittest.mock import patch
from .base import BaseAPITestCase

class SmartSearchAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('stsv_app:smart-search')
        self.client.force_authenticate(user=self.student)

    def test_search_empty_query(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], [])
        
        response = self.client.get(self.url, {'q': '   '})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], [])

    def test_search_exact_feature(self):
        response = self.client.get(self.url, {'q': 'Đổi mật khẩu'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]['title'], 'Đổi mật khẩu')
        self.assertEqual(results[0]['route'], '/profile')
        self.assertEqual(results[0]['type'], 'FEATURE')

    def test_search_fuzzy_feature(self):
        response = self.client.get(self.url, {'q': 'doi mat khau'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('stsv_app.views.search.EventDocument.search')
    def test_search_elasticsearch_mocked(self, mock_search):
        # Mock chuỗi gọi hàm chain: search().query()[:10].params()
        mock_query = mock_search.return_value.query.return_value
        mock_slice = mock_query.__getitem__.return_value
        mock_params = mock_slice.params.return_value
        
        # Mô phỏng danh sách trả về của es_search
        mock_event = type('MockEvent', (), {'id': 999, 'title': 'Hội thảo AI', 'location': 'HT A'})
        mock_params.__iter__.return_value = iter([mock_event])
        
        response = self.client.get(self.url, {'q': 'Hội thảo'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        # Kiểm tra xem event có xuất hiện trong results không
        event_results = [r for r in results if r['type'] == 'EVENT']
        self.assertEqual(len(event_results), 1)
        self.assertEqual(event_results[0]['title'], 'Hội thảo AI')
        self.assertEqual(event_results[0]['id'], '999')

    @patch('stsv_app.views.search.EventDocument.search')
    def test_search_elasticsearch_exception(self, mock_search):
        mock_search.side_effect = Exception("Elasticsearch is down")
        
        response = self.client.get(self.url, {'q': 'Hội thảo'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Sẽ không có lỗi HTTP 500, nhưng phần EVENT không có do fallback đã catch exception
        results = response.data['results']
        event_results = [r for r in results if r['type'] == 'EVENT']
        self.assertEqual(len(event_results), 0)
