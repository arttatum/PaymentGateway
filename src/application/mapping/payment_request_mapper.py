from application.mapping.mapper import Mapper
from core.payment_request_aggregate.PaymentRequest import PaymentRequest


class PaymentRequestMapper:
    """Encapsulates mapping logic required to transform json
    into an instance of PaymentRequest object.

    Returns:
        PaymentRequest: instance of PaymentRequest
    """

    mapper = Mapper.for_type(PaymentRequest)
    # .with_attribute_mappings(
    #     TODO
    # )

    @staticmethod
    def from_json(PaymentRequest_json: dict) -> PaymentRequest:
        return PaymentRequestMapper.mapper.from_json(PaymentRequest_json)
