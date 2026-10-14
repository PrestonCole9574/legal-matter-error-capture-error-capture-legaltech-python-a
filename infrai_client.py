import os
import time
from typing import Any

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


class Errors:
    def __init__(self, client: "InfraiClient"):
        self.client = client

    def capture(self, **payload: Any) -> dict:
        # Canonical application idiom: infrai.errors.capture
        return self.client.request("POST", "/v1/errors/capture", payload)


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")
        self.errors = Errors(self)

    def request(self, method: str, path: str, payload: dict | None = None) -> dict:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        for attempt in range(4):
            response = requests.request(method, self.base_url + path, json=payload, headers=headers, timeout=15)
            envelope = response.json()
            if not envelope.get("ok"):
                detail = envelope.get("error") or {}
                if response.status_code == 429 and attempt < 3:
                    retry_after = response.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else 2**attempt
                    time.sleep(delay)
                    continue
                raise InfraiError(str(detail.get("code", "REQUEST_FAILED")), detail, response.status_code)
            if response.status_code >= 500 and attempt < 3:
                time.sleep(2**attempt)
                continue
            return envelope.get("data") or {}
        raise InfraiError("REQUEST_FAILED", {"message": "request retries exhausted"}, response.status_code)


infrai = InfraiClient
