from corepy.crypto import AeadCryptoProvider, JwtPayload, JwtProvider

from app.common.error_code import BizException, ErrorCode
from app.config import settings

jwt_provider = JwtProvider(settings.ACCESS_TOKEN_PRIVATE_KEY,
                           settings.ACCESS_TOKEN_PUBLIC_KEY,
                           settings.ACCESS_TOKEN_ALGORITHM)


def decode_access_token(token: str) -> JwtPayload:
    payload = jwt_provider.decode_access_token(token)
    if not payload:
        raise BizException.create(ErrorCode.invalid_credentials)
    return payload


if settings.CRYPY_ALGORITHM == "AESGCM":
    _crypt_provider = AeadCryptoProvider.from_aes_gcm(settings.CRYPY_KEY)
else:
    _crypt_provider = AeadCryptoProvider.from_chacha20_poly1305(settings.CRYPY_KEY)


def crypt_encrypt(plain: str) -> str:
    return _crypt_provider.encrypt(plain)


def crypt_decrypt(encrypted: str) -> str:
    return _crypt_provider.decrypt(encrypted)


# CryptStr = Annotated[
#     SecretStr,
#     BeforeValidator(crypt_decrypt), # model_validate
#     PlainSerializer(crypt_encrypt, return_type=str), # model_dump
# ]
