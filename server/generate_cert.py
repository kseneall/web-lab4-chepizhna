from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
from pathlib import Path

# Шляхи
cert_dir = Path("server/cert")
cert_dir.mkdir(parents=True, exist_ok=True)

key_file = cert_dir / "key.pem"
cert_file = cert_dir / "cert.pem"

# Генерація ключа
key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

# Параметри сертифіката
subject = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"UA"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Kyiv"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u"Kyiv"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"MyCompany"),
    x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
])

cert = (
    x509.CertificateBuilder()
    .subject_name(subject)
    .issuer_name(subject)
    .public_key(key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.utcnow())
    .not_valid_after(datetime.utcnow() + timedelta(days=365))
    .sign(key, hashes.SHA256())
)

# Зберегти приватний ключ
with open(key_file, "wb") as f:
    f.write(key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ))

# Зберегти сертифікат
with open(cert_file, "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

print("Сертифікат і ключ створено в server/cert/")
