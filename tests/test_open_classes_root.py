from ms_rrp.operations.open_classes_root import OpenClassesRootRequest, OpenClassesRootResponse, Regsam

from msdsalgs.win32_error import Win32ErrorCode


class TestOpenClassesRootRequest:
    REQUEST = OpenClassesRootRequest.from_bytes(data=bytes.fromhex('0000000000000002'))

    def test_sam_desired(self, request: OpenClassesRootRequest = REQUEST):
        assert request.sam_desired == Regsam(maximum_allowed=True)

    def test_redeserialization(self):
        request = OpenClassesRootRequest.from_bytes(data=bytes(self.REQUEST))
        self.test_sam_desired(request=request)


class TestOpenClassesRootResponse:
    RESPONSE = OpenClassesRootResponse.from_bytes(
        data=bytes.fromhex('00000000da3f1d7efe716e4caf5a0acb5b309b2500000000')
    )

    def test_key_handle(self, response: OpenClassesRootResponse = RESPONSE):
        assert response.key_handle == bytes.fromhex('00000000da3f1d7efe716e4caf5a0acb5b309b25')

    def test_return_code(self, response: OpenClassesRootResponse = RESPONSE):
        assert response.return_code is Win32ErrorCode.ERROR_SUCCESS

    def test_redeserialization(self):
        response = OpenClassesRootResponse.from_bytes(data=bytes(self.RESPONSE))
        self.test_key_handle(response=response)
        self.test_return_code(response=response)
