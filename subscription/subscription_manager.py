import os
import json
import hashlib
from datetime import datetime, timedelta
import platform
import uuid

class SubscriptionManager:
    """
    Handles trial + subscription logic.
    Single source of truth.
    """

    TRIAL_DAYS = 7

    def __init__(self, app_name="MyBot"):
        self.app_name = app_name
        self.base_path = self._get_app_data_path()
        self.data_file = os.path.join(self.base_path, "license.dat")

        os.makedirs(self.base_path, exist_ok=True)

        if not os.path.exists(self.data_file):
            self._create_trial()

    # =========================
    # PUBLIC API (USE ONLY THESE)
    # =========================

    def is_allowed(self) -> bool:
        data = self._load()
        return data["status"] == "ACTIVE"

    def is_trial(self) -> bool:
        data = self._load()
        return data["type"] == "TRIAL"

    def days_left(self) -> int:
        data = self._load()
        expires = datetime.fromisoformat(data["expires_at"])
        return max((expires - datetime.utcnow()).days, 0)

    def lock_reason(self) -> str:
        data = self._load()
        if data["status"] != "ACTIVE":
            return "Trial expired. Please subscribe."
        return ""

    def activate_subscription(self, months: int = 1):
        """
        Call this after payment confirmation
        """
        expires = datetime.utcnow() + timedelta(days=30 * months)
        data = {
            "status": "ACTIVE",
            "type": "SUBSCRIPTION",
            "expires_at": expires.isoformat(),
            "machine_id": self._machine_id()
        }
        self._save(data)

    # =========================
    # INTERNAL
    # =========================

    def _create_trial(self):
        expires = datetime.utcnow() + timedelta(days=self.TRIAL_DAYS)
        data = {
            "status": "ACTIVE",
            "type": "TRIAL",
            "expires_at": expires.isoformat(),
            "machine_id": self._machine_id()
        }
        self._save(data)

    def _load(self) -> dict:
        with open(self.data_file, "r") as f:
            data = json.load(f)

        # Machine binding check
        if data["machine_id"] != self._machine_id():
            return {"status": "LOCKED"}

        # Expiry check
        if datetime.utcnow() > datetime.fromisoformat(data["expires_at"]):
            data["status"] = "LOCKED"
            self._save(data)

        return data

    def _save(self, data: dict):
        with open(self.data_file, "w") as f:
            json.dump(data, f)

    def _machine_id(self) -> str:
        raw = (
            platform.node()
            + platform.system()
            + platform.processor()
            + str(uuid.getnode())
        )
        return hashlib.sha256(raw.encode()).hexdigest()

    def _get_app_data_path(self):
        return os.path.join(
            os.getenv("APPDATA", os.getcwd()),
            self.app_name
        )
