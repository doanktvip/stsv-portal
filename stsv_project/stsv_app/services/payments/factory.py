from .providers.momo import MoMoProvider
from .providers.vnpay import VNPayProvider

class PaymentFactory:
    _gateways = {
        'MOMO': MoMoProvider,
        'VNPAY': VNPayProvider,
    }

    @staticmethod
    def get_payment_gateway(method_name: str):
        method_name = str(method_name).upper()
        gateway_class = PaymentFactory._gateways.get(method_name)
        if not gateway_class:
            raise ValueError(f"Phương thức thanh toán {method_name} không được hỗ trợ.")
        return gateway_class()
