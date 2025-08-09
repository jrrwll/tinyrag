import pytest

from app.common.error_code import BizException, ErrorCode


def test_biz_exception():
    e = BizException.create(ErrorCode.unknown_error, msg=1)
    print(f"\ncontent:\n{e.content()}")

    with pytest.raises(RuntimeError) as exc_info:
        BizException.create(ErrorCode.unknown_error)
    print(f"{exc_info.type} {exc_info.value}")
