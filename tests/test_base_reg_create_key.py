from ms_rrp.operations.base_reg_create_key import BaseRegCreateKeyRequest, BaseRegCreateKeyResponse
from ms_rrp.structures.reg_options import RegOptions
from ms_rrp.structures.regsam import Regsam
from ms_rrp.structures.disposition import Disposition

from msdsalgs.win32_error import Win32ErrorCode


class TestBaseRegCreateKeyRequest:
    REQUEST = BaseRegCreateKeyRequest.from_bytes(
        data=bytes.fromhex('00000000da3f1d7efe716e4caf5a0acb5b309b250a000a00dbdc00000500000000000000050000004200450054004f000000abab00000000000000000100000000000002836300000000000000000000000000000000000000aaaaaa897b000001000000')
    )

    def test_key_handle(self, request: BaseRegCreateKeyRequest = REQUEST):
        assert request.key_handle == bytes.fromhex('00000000da3f1d7efe716e4caf5a0acb5b309b25')

    def test_sub_key_name(self, request: BaseRegCreateKeyRequest = REQUEST):
        assert request.sub_key_name == 'BETO'

    def test_class_name(self, request: BaseRegCreateKeyRequest = REQUEST):
        assert request.class_name == ''

    def test_options(self, request: BaseRegCreateKeyRequest = REQUEST):
        assert request.options == RegOptions(volatile=True)

    def test_sam_desired(self, request: BaseRegCreateKeyRequest = REQUEST):
        assert request.sam_desired == Regsam(maximum_allowed=True)

    def test_security_attributes(self, request: BaseRegCreateKeyRequest = REQUEST):
        security_attributes = request.security_attributes

        assert security_attributes.rpc_security_descriptor.security_descriptor is None
        assert not security_attributes.inherit_handle

    def test_disposition(self, request: BaseRegCreateKeyRequest = REQUEST):
        assert request.disposition is Disposition.REG_CREATED_NEW_KEY

    def test_redeserialization(self):
        request = BaseRegCreateKeyRequest.from_bytes(data=bytes(self.REQUEST))

        self.test_key_handle(request=request)
        self.test_sub_key_name(request=request)
        self.test_class_name(request=request)
        self.test_options(request=request)
        self.test_sam_desired(request=request)
        self.test_security_attributes(request=request)
        self.test_disposition(request=request)


class TestBaseRegCreateKeyResponse:
    RESPONSE = BaseRegCreateKeyResponse.from_bytes(
        data=bytes.fromhex('00000000084a756c463558459d00e2b2e277b6d9000002000200000000000000')
    )

    def test_key_handle(self, response: BaseRegCreateKeyResponse = RESPONSE):
        assert response.key_handle == bytes.fromhex('00000000084a756c463558459d00e2b2e277b6d9')

    def test_disposition(self, response: BaseRegCreateKeyResponse = RESPONSE):
        assert response.disposition is Disposition.REG_OPENED_EXISTING_KEY

    def test_return_code(self, response: BaseRegCreateKeyResponse = RESPONSE):
        assert response.return_code is Win32ErrorCode.ERROR_SUCCESS

    def test_redeserialization(self):
        response = BaseRegCreateKeyResponse.from_bytes(data=bytes(self.RESPONSE))

        self.test_key_handle(response=response)
        self.test_disposition(response=response)
        self.test_return_code(response=response)
