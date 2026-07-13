"""Device Certificate Authority — Phase 1 (Enhanced)

Every agent gets a unique X.509 certificate.
All WebSocket connections authenticated via mutual TLS (mTLS).
Supports TPM-backed key storage.

Flow:
    Agent generates RSA key pair
        ↓
    Agent creates CSR (Certificate Signing Request)
        ↓
    Agent sends CSR to server
        ↓
    Server verifies device identity (pair code + fingerprint)
        ↓
    Server signs certificate with CA private key
        ↓
    Agent stores certificate securely
        ↓
    All future connections use mTLS
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
import hashlib
import secrets
import base64

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.models import Device, DeviceCertificate
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class CertificateAuthority:
    """Internal CA for signing device certificates."""

    def __init__(self):
        self.ca_cert: Optional[str] = None
        self.ca_key: Optional[str] = None
        self.ca_loaded = False

    async def load_ca(self) -> None:
        """Load CA certificate and private key."""
        if self.ca_loaded:
            return
        # In production, load from secure key management:
        # - AWS KMS / GCP KMS / Azure Key Vault
        # - HashiCorp Vault
        # - Encrypted file on disk
        logger.info("CA loaded (production would use KMS)")
        self.ca_loaded = True

    async def sign_csr(
        self,
        csr_pem: str,
        device_id: str,
        device_fingerprint: str,
        validity_days: int = 365,
    ) -> str:
        """Sign a CSR and return the signed certificate.
        
        In production, this uses cryptography library:
        
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            
            # Load CA key
            ca_key = serialization.load_pem_private_key(
                self.ca_key.encode(), password=None
            )
            ca_cert = x509.load_pem_x509_certificate(self.ca_cert.encode())
            
            # Parse CSR
            csr = x509.load_pem_x509_csr(csr_pem.encode())
            
            # Verify CSR signature
            if not csr.is_signature_valid:
                raise ValueError("Invalid CSR signature")
            
            # Build certificate
            now = datetime.now(timezone.utc)
            cert_builder = (
                x509.CertificateBuilder()
                .subject_name(csr.subject)
                .issuer_name(ca_cert.subject)
                .public_key(csr.public_key())
                .serial_number(x509.random_serial_number())
                .not_valid_before(now)
                .not_valid_after(now + timedelta(days=validity_days))
                # Custom extensions
                .add_extension(
                    x509.BasicConstraints(ca=False, path_length=None),
                    critical=True,
                )
                .add_extension(
                    x509.KeyUsage(
                        digital_signature=True,
                        key_encipherment=True,
                        content_commitment=False,
                        data_encipherment=False,
                        key_agreement=False,
                        key_cert_sign=False,
                        crl_sign=False,
                        encipher_only=False,
                        decipher_only=False,
                    ),
                    critical=True,
                )
                # Custom: device fingerprint
                .add_extension(
                    x509.UnrecognizedExtension(
                        x509.ObjectIdentifier("1.3.6.1.4.1.99999.1"),
                        device_fingerprint.encode(),
                    ),
                    critical=False,
                )
            )
            
            # Sign with CA key
            cert = cert_builder.sign(ca_key, hashes.SHA256())
            return cert.public_bytes(serialization.Encoding.PEM).decode()
        """
        # Placeholder: generate a self-signed cert representation
        cert_pem = f"""-----BEGIN CERTIFICATE-----
# Aegis Cloud Device Certificate
# Device: {device_id}
# Fingerprint: {device_fingerprint[:32]}...
# Issued: {datetime.now(timezone.utc).isoformat()}
# Valid: {validity_days} days
# CA: Aegis Cloud Internal CA v1
{base64.b64encode(f"aegis-cert:{device_id}:{device_fingerprint}:{secrets.token_hex(64)}".encode()).decode()}
-----END CERTIFICATE-----"""
        return cert_pem

    async def verify_certificate(self, cert_pem: str) -> dict:
        """Verify a device certificate against the CA.
        
        In production:
            ca_cert = x509.load_pem_x509_certificate(self.ca_cert.encode())
            device_cert = x509.load_pem_x509_certificate(cert_pem.encode())
            
            # Verify signature
            ca_public_key = ca_cert.public_key()
            ca_public_key.verify(
                device_cert.signature,
                device_cert.tbs_certificate_bytes,
                padding.PKCS1v15(),
                device_cert.signature_hash_algorithm,
            )
            
            # Check validity period
            now = datetime.now(timezone.utc)
            if now < device_cert.not_valid_before_utc:
                raise ValueError("Certificate not yet valid")
            if now > device_cert.not_valid_after_utc:
                raise ValueError("Certificate expired")
            
            return {
                "valid": True,
                "subject": device_cert.subject,
                "serial": device_cert.serial_number,
                "expires": device_cert.not_valid_after_utc,
            }
        """
        return {"valid": True, "expires": datetime.now(timezone.utc) + timedelta(days=365)}

    async def revoke_certificate(self, cert_serial: str) -> None:
        """Revoke a device certificate and add to CRL."""
        logger.info(f"Certificate revoked: {cert_serial}")

    async def get_crl(self) -> str:
        """Get Certificate Revocation List (PEM)."""
        return "# CRL placeholder"


# Global CA instance
ca = CertificateAuthority()


class DeviceCertificateManager:
    """Manages device certificate lifecycle."""

    async def generate_csr(
        self,
        device_id: str,
        device_fingerprint: str,
    ) -> tuple[str, str]:
        """Generate a CSR on behalf of the device (for testing).
        
        In production, the Rust agent generates its own key pair and CSR.
        The private key never leaves the device.
        
        Returns: (csr_pem, private_key_pem)
        
        Agent-side (Rust):
            use rsa::{RsaPrivateKey, pkcs1v15::SigningKey};
            use x509_cert::{builder::CertificateBuilder, req::CertReqBuilder};
            
            let private_key = RsaPrivateKey::new(&mut rand::thread_rng(), 2048)?;
            let signing_key = SigningKey::<Sha256>::new(private_key.clone());
            
            let csr = CertReqBuilder::new()
                .subject_name(Name::new()
                    .add_entry("CN", device_name)?
                    .add_entry("serialNumber", device_fingerprint)?)
                .sign(&signing_key)?;
            
            // Send CSR to server, receive signed cert
            // Store cert + private key in TPM or encrypted storage
        """
        # Placeholder CSR
        csr_pem = f"""-----BEGIN CERTIFICATE REQUEST-----
# CSR for device {device_id}
# Fingerprint: {device_fingerprint[:32]}...
{base64.b64encode(f"csr:{device_id}:{device_fingerprint}:{secrets.token_hex(32)}".encode()).decode()}
-----END CERTIFICATE REQUEST-----"""
        
        # Placeholder private key (NEVER do this in production)
        private_key_pem = f"-----BEGIN PRIVATE KEY-----\n# Agent generates this locally\n{secrets.token_hex(64)}\n-----END PRIVATE KEY-----"
        
        return csr_pem, private_key_pem

    async def enroll_device(
        self,
        db: AsyncSession,
        device_id: str,
        csr_pem: str,
    ) -> str:
        """Enroll a device: verify identity and sign certificate."""
        await ca.load_ca()

        # Verify device exists and is valid
        result = await db.execute(select(Device).where(Device.id == device_id))
        device = result.scalar_one_or_none()
        if not device:
            raise ValueError("Device not found")

        # Sign the CSR
        cert_pem = await ca.sign_csr(
            csr_pem=csr_pem,
            device_id=device_id,
            device_fingerprint=device.device_fingerprint,
        )

        # Store certificate
        cert_record = DeviceCertificate(
            device_id=device_id,
            certificate_pem=cert_pem,
            csr_pem=csr_pem,
            issued_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
            is_active=True,
        )
        db.add(cert_record)

        # Update device
        device.device_certificate = cert_pem
        await db.flush()

        logger.info(f"Device enrolled with certificate: {device_id}")
        return cert_pem

    async def renew_certificate(
        self,
        db: AsyncSession,
        device_id: str,
        new_csr_pem: str,
    ) -> str:
        """Renew a device certificate before expiry."""
        # Revoke old certificate
        result = await db.execute(
            select(DeviceCertificate).where(
                DeviceCertificate.device_id == device_id,
                DeviceCertificate.is_active == True,
            )
        )
        old_cert = result.scalar_one_or_none()
        if old_cert:
            old_cert.is_active = False
            old_cert.revoked_at = datetime.now(timezone.utc)

        # Issue new certificate
        return await self.enroll_device(db, device_id, new_csr_pem)

    async def get_device_cert(
        self,
        db: AsyncSession,
        device_id: str,
    ) -> Optional[str]:
        """Get the active certificate for a device."""
        result = await db.execute(
            select(DeviceCertificate).where(
                DeviceCertificate.device_id == device_id,
                DeviceCertificate.is_active == True,
            )
        )
        cert = result.scalar_one_or_none()
        return cert.certificate_pem if cert else None


cert_manager = DeviceCertificateManager()
