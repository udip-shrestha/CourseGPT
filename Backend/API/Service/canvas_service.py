import os
import jwt
import base64
import httpx
from typing import Dict, List
from pathlib import Path
from fastapi.responses import RedirectResponse
from fastapi import status
from cryptography.hazmat.primitives import serialization


class CanvasService:
    """Service handling minimal Canvas LTI interactions and JWK publishing.

    - Signs JWTs with a configured RSA private key
    - Publishes the RSA public key as a JWK
    - Provides a placeholder file ingestion helper
    """

    def __init__(self):
        self.private_key_b64 = os.getenv("CANVAS_PRIVATE_KEY_B64")
        self.public_key_b64 = os.getenv("CANVAS_PUBLIC_KEY_B64")
        self.kid = os.getenv("CANVAS_KEY_ID", "coursegpt-key-1")
        
        if not self.public_key_b64:
            raise RuntimeError("CANVAS_PUBLIC_KEY_B64 not set")

    def _load_public_key(self) -> str:
        decoded = base64.b64decode(self.public_key_b64)
        return serialization.load_pem_public_key(decoded)

    def _b64u(self, b: bytes) -> str:
        return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii") # Convert to Base64 URL safe string without padding

    def redirect_to(self, base_url: str, path: str) -> RedirectResponse:
        """Return a redirect response to the provided base_url + path."""
        return RedirectResponse(url=f"{base_url}{path}", status_code=status.HTTP_302_FOUND)
    
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
    
    async def get_canvas_modules(self, canvas_course_id: str, canvas_token: str):
        numeric_id = await self.get_canvas_numeric_id(canvas_course_id, canvas_token)

        url = f"https://iastate-studentdev.instructure.com/api/v1/courses/{numeric_id}/modules"

        params = { "include[]": "items"}

        headers = { "Authorization": f"Bearer {canvas_token}"}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

        if response.status_code != 200:
            raise RuntimeError(f"Canvas API error: {response.text}")

        return response.json()
    
    async def get_canvas_numeric_id(self, canvas_course_id: str, canvas_token: str) -> int:
        url = f"https://iastate-studentdev.instructure.com:{canvas_course_id}"

        headers = { "Authorization": f"Bearer {canvas_token}"}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        if response.status_code != 200:
            raise RuntimeError(f"Canvas API error: {response.text}")

        data = response.json()
        return data.get("id")

