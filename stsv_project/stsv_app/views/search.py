from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from stsv_app.documents import EventDocument
from elasticsearch_dsl import Q
import logging
import difflib

logger = logging.getLogger(__name__)

class SmartSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.GET.get('q', '').strip()
        if not query:
            return Response({'results': []})
            
        results = []

        # 1. Tìm kiếm tính năng hệ thống (Cứng)
        features = [
            # Sinh viên
            {'title': 'Đóng học phí', 'route': '/finance'},
            {'title': 'Thanh toán học phí', 'route': '/finance'},
            {'title': 'Sổ Đoàn', 'route': '/youth-union'},
            {'title': 'Hồ sơ Đoàn viên', 'route': '/youth-union'},
            {'title': 'Điểm rèn luyện', 'route': '/study-info'},
            {'title': 'Lịch học', 'route': '/study-info'},
            {'title': 'Lịch thi', 'route': '/study-info'},
            {'title': 'Báo cáo cơ sở vật chất', 'route': '/support'},
            {'title': 'Khiếu nại', 'route': '/support'},
            {'title': 'Quét mã QR', 'route': '/qr-scanner'},
            {'title': 'Điểm danh', 'route': '/qr-scanner'},
            {'title': 'Thông báo', 'route': '/notifications'},
            {'title': 'Hồ sơ cá nhân', 'route': '/profile'},
            {'title': 'Đổi mật khẩu', 'route': '/profile'},
            
            # Admin & Ban Tổ Chức (CLB)
            {'title': 'Quản trị tài khoản', 'route': '/account-management'},
            {'title': 'Phân quyền người dùng', 'route': '/account-management'},
            {'title': 'Quản lý sự kiện', 'route': '/events'},
            {'title': 'Đề xuất sự kiện', 'route': '/events'},
            {'title': 'Cấu hình điểm rèn luyện', 'route': '/training-point-config'},
            {'title': 'Cấu hình hệ thống', 'route': '/system-config'},
            {'title': 'Dòng tiền & Báo cáo', 'route': '/admin-finance'},
        ]
        
        # Tìm kiếm tính năng (hỗ trợ sai lỗi chính tả nhẹ bằng difflib)
        query_lower = query.lower()
        feature_titles = [f['title'].lower() for f in features]
        
        # Tìm các tính năng có chứa từ khóa (chính xác)
        exact_matches = [f for f in features if query_lower in f['title'].lower()]
        
        # Tìm các tính năng gần giống (Fuzzy / Sai chính tả)
        close_titles = difflib.get_close_matches(query_lower, feature_titles, n=3, cutoff=0.5)
        fuzzy_matches = [f for f in features if f['title'].lower() in close_titles and f not in exact_matches]
        
        for f in exact_matches + fuzzy_matches:
            results.append({
                'id': f"feature_{f['route']}",
                'title': f['title'],
                'type': 'FEATURE',
                'route': f['route'],
                'subtitle': 'Tính năng hệ thống'
            })

        # 2. Tìm kiếm Sự kiện (Bằng Elasticsearch)
        try:
            # Tìm kiếm mờ (Fuzzy Search) trên các trường title (ưu tiên x3), description, location
            q = Q('multi_match', query=query, fields=['title^3', 'description', 'location'], fuzziness='AUTO')
            es_search = EventDocument.search().query(q)[:10].params(request_timeout=2)
            
            for event in es_search:
                results.append({
                    'id': str(event.id),
                    'title': event.title,
                    'type': 'EVENT',
                    'route': '/events', # Sẽ sửa lại nếu có màn hình chi tiết sự kiện sau
                    'subtitle': f"Sự kiện • {event.location if hasattr(event, 'location') else ''}"
                })
        except Exception as e:
            logger.error(f"Lỗi Elasticsearch: {e}")
            # Có thể fallback về MySQL icontains ở đây nếu muốn an toàn 100%
            
        return Response({'results': results})
