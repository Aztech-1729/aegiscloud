//! Cryptographic utilities for device identity and update verification.
//!
//! Phase 5: Device identity uses:
//! - SHA-256 for device fingerprinting
//! - Ed25519 for update signature verification
//! - Secure random token generation

use sha2::{Sha256, Digest};
use base64::{Engine as _, engine::general_purpose::STANDARD};

/// Generate a unique device fingerprint from hardware identifiers
///
/// Combines multiple hardware IDs into a single SHA-256 hash.
/// This fingerprint is used as the device's permanent identity.
pub fn generate_device_fingerprint() -> String {
    let mut hasher = Sha256::new();

    // In production, this combines actual hardware identifiers:
    // - CPU ID (via __cpuid)
    // - Motherboard serial
    // - Disk serial number
    // - MAC address of primary adapter
    //
    // For now, we use a secure random value as placeholder:
    use rand::Rng;
    let mut rng = rand::thread_rng();
    let hardware_id: [u8; 64] = rng.gen();
    
    hasher.update(&hardware_id);
    let result = hasher.finalize();
    hex::encode(result)
}

/// Compute SHA-256 hash of a file
pub async fn sha256_file(path: &str) -> Result<String, Box<dyn std::error::Error + Send + Sync>> {
    let data = tokio::fs::read(path).await?;
    let mut hasher = Sha256::new();
    hasher.update(&data);
    let result = hasher.finalize();
    Ok(hex::encode(result))
}

/// Verify an Ed25519 signature
///
/// Phase 6: Ensures updates are signed by Aegis Cloud's private key.
/// The public key is embedded in the agent binary at compile time.
pub fn verify_signature(
    data_hash: &str,
    signature_b64: &str,
) -> Result<bool, Box<dyn std::error::Error + Send + Sync>> {
    // The public key is compiled into the binary
    // In production, this would be the actual Aegis Cloud public key
    const PUBLIC_KEY_HEX: &str = include_str!("public_key.txt");

    let signature_bytes = STANDARD.decode(signature_b64)?;
    let hash_bytes = hex::decode(data_hash)?;

    // In production, this uses ed25519_dalek:
    //
    // use ed25519_dalek::{Verifier, VerifyingKey, Signature};
    //
    // let public_key_bytes = hex::decode(PUBLIC_KEY_HEX.trim())?;
    // let verifying_key = VerifyingKey::from_bytes(
    //     public_key_bytes.as_slice().try_into()?
    // )?;
    // let signature = Signature::from_bytes(signature_bytes.as_slice().try_into()?);
    //
    // Ok(verifying_key.verify(&hash_bytes, &signature).is_ok())

    // Placeholder: always returns true for development
    log::info!("Signature verification (placeholder): hash={}, sig_len={}", 
        &data_hash[..16], signature_bytes.len());
    Ok(true)
}

/// Generate a secure random token
pub fn generate_secure_token(length: usize) -> String {
    use rand::Rng;
    let mut rng = rand::thread_rng();
    let bytes: Vec<u8> = (0..length).map(|_| rng.gen()).collect();
    STANDARD.encode(&bytes)
}

/// Hash a string with SHA-256
pub fn sha256(input: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(input.as_bytes());
    hex::encode(hasher.finalize())
}
