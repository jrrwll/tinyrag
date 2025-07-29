from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from app.common.security import create_access_token, get_password_hash, \
    decode_access_token
from app.config import settings


def generate_rsa_keys() -> tuple[str, str]:
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    print(f"private_pem={private_pem.decode()}")

    public_key: rsa.RSAPublicKey = private_key.public_key()
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    print(f"pem={pem.decode()}")

    return pem.decode(), private_pem.decode()


def test_security() -> None:
    print(f"\npassword_hash={get_password_hash('tinyrag')}")

    access_token = create_access_token("test")
    print(f"\naccess_token={access_token}")

    payload = decode_access_token(access_token)
    print(f"\npayload={payload}")
