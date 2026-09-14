import logging
import difflib
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from stsv_app.documents import EventDocument, NotificationDocument, OrgProfileDocument
from elasticsearch_dsl import Q

logger = logging.getLogger(__name__)

class SmartSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.GET.get('q', '').strip()
        if not query:
            return Response({
                'status': 'success',
                'data': {'results': []}
            })
            
        results = []

        # 1. Tìm kiếm tính năng hệ thống (Cứng)
        features = [
            # Sinh viên
            {'title': 'Đóng Đoàn phí', 'route': '/finance'},
            {'title': 'Nộp quỹ lớp', 'route': '/finance'},
            {'title': 'Sổ Đoàn', 'route': '/youth-union'},
            {'title': 'Hồ sơ Đoàn viên', 'route': '/youth-union'},
            {'title': 'Điểm rèn luyện', 'route': '/study-info'},
            {'title': 'Báo cáo cơ sở vật chất', 'route': '/support'},
            {'title': 'Khiếu nại', 'route': '/support'},
            {'title': 'Quét mã QR', 'route': '/qr-scanner'},
            {'title': 'Điểm danh', 'route': '/qr-scanner'},
            {'title': 'Thông báo', 'route': '/notifications'},
            {'title': 'Hồ sơ cá nhân', 'route': '/profile'},
            {'title': 'Đổi mật khẩu', 'route': '/profile'},
            
            # Admin & Ban Tổ Chức (Khoa, Đoàn, CLB)
            {'title': 'Hồ sơ Tổ chức', 'route': '/org-profile'},
            {'title': 'Duyệt Sự kiện', 'route': '/events-approval'},
            {'title': 'Quản lý Sự kiện', 'route': '/events'},
            {'title': 'Thống kê Phong trào', 'route': '/statistics'},
            {'title': 'Quản lý ĐRL Cấp Khoa', 'route': '/training-point-config'},
            {'title': 'Khảo sát & Báo cáo', 'route': '/reports'},
            {'title': 'Quản trị tài khoản', 'route': '/account-management'},
            {'title': 'Cấu hình hệ thống', 'route': '/system-config'},
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
            q_event = Q('multi_match', query=query, fields=['title^3', 'description', 'location'], fuzziness='AUTO')
            es_search_event = EventDocument.search().query(q_event)[:5].params(request_timeout=2)
            
            for event in es_search_event:
                event_dict = event.to_dict()
                results.append({
                    'id': f"event_{event.meta.id}",
                    'title': event_dict.get('title', ''),
                    'type': 'EVENT',
                    'route': '/events',
                    'subtitle': f"Sự kiện • {event_dict.get('location', '')}"
                })
        except Exception as e:
            logger.error(f"Lỗi Elasticsearch (Event): {e}")

        # 3. Tìm kiếm Thông báo (Bằng Elasticsearch)
        try:
            q_noti = Q('multi_match', query=query, fields=['title^3', 'message'], fuzziness='AUTO')
            es_search_noti = NotificationDocument.search().query(q_noti)[:5].params(request_timeout=2)
            
            for noti in es_search_noti:
                noti_dict = noti.to_dict()
                results.append({
                    'id': f"noti_{noti.meta.id}",
                    'title': noti_dict.get('title', ''),
                    'type': 'NOTIFICATION',
                    'route': '/notifications',
                    'subtitle': 'Thông báo hệ thống'
                })
        except Exception as e:
            logger.error(f"Lỗi Elasticsearch (Notification): {e}")

        # 4. Tìm kiếm Tổ chức / CLB (Bằng Elasticsearch)
        try:
            q_org = Q('multi_match', query=query, fields=['org_name^3', 'description'], fuzziness='AUTO')
            es_search_org = OrgProfileDocument.search().query(q_org)[:5].params(request_timeout=2)
            
            for org in es_search_org:
                org_dict = org.to_dict()
                results.append({
                    'id': f"org_{org.meta.id}",
                    'title': org_dict.get('org_name', ''),
                    'type': 'ORGANIZATION',
                    'route': '/org-profile',
                    'subtitle': f"Tổ chức • {org_dict.get('org_type', 'Khác')}"
                })
        except Exception as e:
            logger.error(f"Lỗi Elasticsearch (OrgProfile): {e}")
            
        return Response({
            'status': 'success',
            'data': {
                'results': results
            }
        })
