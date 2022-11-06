import pytest

from core.payment_request_aggregate.value_objects.MerchantId import MerchantId
from shared_kernel.exceptions.DomainException import DomainException


def test_merchant_id_must_be_uuid4():
    not_uuid_4 = "12356789"

    with pytest.raises(DomainException) as e:
        MerchantId(not_uuid_4)

    assert "Merchant ID must be a UUID-4." in e.value.messages[0]
