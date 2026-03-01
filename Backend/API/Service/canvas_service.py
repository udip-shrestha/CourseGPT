import os
import jwt
import base64
from typing import Dict, List
from pathlib import Path
from cryptography.hazmat.primitives import serialization


class CanvasService:
    """Service handling minimal Canvas LTI interactions and JWK publishing.

    - Signs JWTs with a configured RSA private key
    - Publishes the RSA public key as a JWK
    - Provides a placeholder file ingestion helper
    """

    def __init__(self, private_key_path: str = None, public_key_path: str = None, kid: str = "1"):
        backend_root = Path(__file__).resolve().parents[2]
        self.private_key_path = os.getenv("CANVAS_PRIVATE_KEY_PATH") or str(backend_root / "private.key")
        self.public_key_path = os.getenv("CANVAS_PUBLIC_KEY_PATH") or str(backend_root / "public.key")
        self.kid = os.getenv("CANVAS_KEY_ID", "coursegpt-key-1")

        # Load keys lazily
        self._private_key_pem = None
        self._public_key_pem = None

    def _load_private_key(self) -> str:
        if self._private_key_pem is None:
            with open(self.private_key_path, "rb") as fh:
                self._private_key_pem = serialization.load_pem_private_key(fh.read())
        return self._private_key_pem

    def _load_public_key(self) -> str:
        if self._public_key_pem is None:
            with open(self.public_key_path, "rb") as fh:
                self._public_key_pem = serialization.load_pem_public_key(fh.read())
        return self._public_key_pem

    def _b64u(self, b: bytes) -> str:
        return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii") # Convert to Base64 URL safe string without padding

    def public_jwk(self) -> Dict:
        """Return a JWK (RSA) derived from the configured public key PEM."""
        pub_key = self._load_public_key()
        numbers = pub_key.public_numbers()
        n = numbers.n
        e = numbers.e

        n_bytes = n.to_bytes((n.bit_length() + 7) // 8, byteorder="big")
        e_bytes = e.to_bytes((e.bit_length() + 7) // 8, byteorder="big")

        jwk = {
            "kty": "RSA",
            "use": "sig",
            "alg": "RS256",
            "kid": self.kid,
            "n": self._b64u(n_bytes),
            "e": self._b64u(e_bytes),
        }
        return jwk

    def fetch_canvas_files(self, canvas_token: str = None) -> List[Dict]:
        """Placeholder: return an empty list or later call Canvas API using `canvas_token`.

        Implementers can expand this to call Canvas REST API and ingest files.
        """
        return []
