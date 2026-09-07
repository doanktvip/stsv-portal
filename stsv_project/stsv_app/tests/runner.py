import logging
from django.test.runner import DiscoverRunner

class SeedRunner(DiscoverRunner):
    def setup_databases(self, **kwargs):
        # Tắt toàn bộ logging (các câu print lỗi từ logger) khi chạy test
        logging.disable(logging.CRITICAL)
        
        # 1. Hệ thống mặc định của Django sẽ tạo Database Ảo (Chạy migrations)
        result = super().setup_databases(**kwargs)
        
        # 2. Sau khi DB ảo đã sẵn sàng nhưng CHƯA chạy bài test nào, ta tiến hành Seed dữ liệu
        print("\n=======================================================")
        print("BẮT ĐẦU NẠP DỮ LIỆU ẢO (SEEDING) 1 LẦN DUY NHẤT...")
        
        from stsv_app.seeders import (
            seed_core,
            seed_users,
            seed_events,
            seed_academics,
            seed_finance,
        )
        
        seed_core()
        seed_users(num_students=5)
        seed_events(num_events=2)
        seed_academics(num_students=5)
        seed_finance()
        
        print("HOÀN TẤT NẠP DỮ LIỆU. BẮT ĐẦU CHẠY CÁC BÀI TEST...")
        print("=======================================================\n")
        
        # 3. Trả về cấu trúc Database để các bài Test được tiến hành (Mỗi test case sẽ rollback về trạng thái này sau khi chạy)
        return result
