from decimal import Decimal

from application.mapping.mapper import Mapper
from core.payment_request_aggregate.PaymentRequest import PaymentRequest
from core.payment_request_aggregate.value_objects.CardNumber import CardNumber
from core.payment_request_aggregate.value_objects.Currency import Currency
from core.payment_request_aggregate.value_objects.CVV import CVV
from core.payment_request_aggregate.value_objects.ExpiryDate import ExpiryDate
from core.payment_request_aggregate.value_objects.MerchantId import MerchantId
from core.payment_request_aggregate.value_objects.MonetaryAmount import MonetaryAmount
from shared_kernel.lambda_logging import get_logger


class PaymentRequestMapper:
    """Encapsulates mapping logic required to transform json
    into an instance of PaymentRequest object.

    Returns:
        PaymentRequest: instance of PaymentRequest
    """

    mapper = Mapper.for_type(PaymentRequest).with_attribute_mappings(
        card_number=Mapper.for_type(CardNumber),
        merchant_id=Mapper.for_type(MerchantId),
        expiry_date=Mapper.for_type(ExpiryDate),
        cvv=Mapper.for_type(CVV),
        amount=Mapper.for_type(MonetaryAmount).with_attribute_mappings(
            currency=Mapper.for_type(Currency), amount=Mapper.for_type(Decimal)
        ),
    )

    @staticmethod
    def from_json(PaymentRequest_json: dict) -> PaymentRequest:
        get_logger().info("Mapping JSON to PaymentRequest model.")
        return PaymentRequestMapper.mapper.from_json(PaymentRequest_json)
