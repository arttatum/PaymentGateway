import pytest

from core.payment_request_aggregate.value_objects.AcquiringBankResponse import (
    AcquiringBankResponse,
)
from shared_kernel.exceptions.DomainException import DomainException


@pytest.mark.parametrize("valid_response", AcquiringBankResponse._valid_statuses)
def test_valid_statuses_are_allowed(valid_response):
    acquiring_bank_response = AcquiringBankResponse(valid_response)

    assert acquiring_bank_response.value == valid_response


def test_unsupported_status_raises_domain_exception():
    invalid_response = "Other response..."
    with pytest.raises(DomainException) as e:
        AcquiringBankResponse(invalid_response)

    assert "Response message: Other response... is not supported." in e.value.messages[0]
