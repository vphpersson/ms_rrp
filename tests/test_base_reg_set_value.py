from ms_rrp.operations.base_reg_set_value import BaseRegSetValueRequest, BaseRegSetValueResponse
from ms_rrp.structures.reg_value_type import RegValueType

from msdsalgs.win32_error import Win32ErrorCode


class TestBaseRegSetValueRequest:
    REQUEST = BaseRegSetValueRequest.from_bytes(
        data=bytes.fromhex('00000000084a756c463558459d00e2b2e277b6d90c000c00532200000600000000000000060000004200450054004f003200000004000000040000000100000004000000')
    )

    def test_key_handle(self, request: BaseRegSetValueRequest = REQUEST):
        assert request.key_handle == bytes.fromhex('00000000084a756c463558459d00e2b2e277b6d9')

    def test_sub_key_name(self, request: BaseRegSetValueRequest = REQUEST):
        assert request.sub_key_name == 'BETO2'

    def test_value_type(self, request: BaseRegSetValueRequest = REQUEST):
        assert request.value_type is RegValueType.REG_DWORD

    def test_value(self, request: BaseRegSetValueRequest = REQUEST):
        assert request.value == b'\x01\x00\x00\x00'

    def test_redeserialization(self):
        request = BaseRegSetValueRequest.from_bytes(data=bytes(self.REQUEST))

        self.test_key_handle(request=request)
        self.test_sub_key_name(request=request)
        self.test_value_type(request=request)
        self.test_value(request=request)


class TestBaseRegSetValueResponse:
    RESPONSE = BaseRegSetValueResponse.from_bytes(data=bytes.fromhex('00000000'))

    def test_return_code(self, response: BaseRegSetValueResponse = RESPONSE):
        assert response.return_code is Win32ErrorCode.ERROR_SUCCESS

    def test_redeserialization(self):
        response = BaseRegSetValueResponse.from_bytes(data=bytes(self.RESPONSE))

        self.test_return_code(response=response)
