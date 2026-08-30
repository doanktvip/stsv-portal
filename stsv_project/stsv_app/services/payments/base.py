from abc import ABC, abstractmethod

class BasePaymentProvider(ABC):
    @abstractmethod
    def generate_payment_url(self, transaction_id: str, amount: float, order_info: str, return_url: str) -> str:
        """
        Khởi tạo giao dịch.
        Trả về URL thanh toán.
        """
        pass

    @abstractmethod
    def verify_webhook(self, request_data: dict) -> bool:
        """
        Xác thực Webhook/IPN trả về từ đối tác.
        Trả về True nếu hợp lệ, False nếu sai chữ ký/dữ liệu.
        """
        pass
