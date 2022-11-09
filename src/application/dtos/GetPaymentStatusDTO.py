from core.payment_request_aggregate.PaymentRequest import PaymentRequest


class GetPaymentStatusDTO:
    def __init__(self, payment_request: PaymentRequest, status: str):
        self.json = {
            "payment_details": {
                "id": payment_request.id,
                "card_number": payment_request.card_number.to_masked_card_number(),
                "cvv": payment_request.cvv.value,
                "expiry_date": str(payment_request.expiry_date),
                "amount": payment_request.amount.amount,
                "currency": payment_request.amount.currency.value,
            },
            "status": status,
        }
