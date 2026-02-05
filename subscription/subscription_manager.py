import os
import json
import hashlib
import shutil
from datetime import datetime, timedelta
import platform
import uuid

class SubscriptionManager:
    """
    Handles trial + subscription logic.
    Single source of truth.
    """

    TRIAL_DAYS = 7

    def __init__(self, app_name="MyBot", legacy_app_name=None):
        self.app_name = app_name
        self.base_path = self._get_app_data_path(app_name)
        self.data_file = os.path.join(self.base_path, "license.dat")

        os.makedirs(self.base_path, exist_ok=True)

        if not os.path.exists(self.data_file):
            self._migrate_legacy(legacy_app_name)
        # Do not auto-start the trial; let the app explicitly start it.

    # =========================
    # PUBLIC API (USE ONLY THESE)
    # =========================

    def is_allowed(self) -> bool:
        data = self._load()
        return data["status"] == "ACTIVE"

    def needs_trial_start(self) -> bool:
        data = self._load()
        return data.get("status") == "MISSING"

    def is_trial(self) -> bool:
        data = self._load()
        return (
            data.get("status") == "ACTIVE"
            and data.get("type") == "TRIAL"
        )

    def days_left(self) -> int:
        data = self._load()
        if data.get("status") != "ACTIVE":
            return 0
        if "expires_at" not in data:
            return 0
        expires = datetime.fromisoformat(data["expires_at"])
        return max((expires - datetime.utcnow()).days, 0)

    def lock_reason(self) -> str:
        data = self._load()
        if data["status"] == "MISSING":
            return "Trial not started. Please start your trial."
        if data["status"] != "ACTIVE":
            return "Trial expired. Please subscribe."
        return ""

    def start_trial(self) -> bool:
        """
        Start the trial only if no license data exists yet.
        Returns True if the trial was created, False otherwise.
        """
        if os.path.exists(self.data_file):
            return False
        self._create_trial()
        self._ensure_database()
        return True

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

    def _ensure_database(self):
        try:
            from all_variable import Variable
            db_path = Variable.DATABASE
            db_dir = os.path.dirname(db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)

            # Importing runs the table-creation script.
            from database_creation import make_database  # noqa: F401

            if self._database_has_data(db_path):
                return

            from database_creation import grab_data
            grab_data.DataCollection().collect_data("BTCUSDT")
        except Exception:
            pass

    def _database_has_data(self, db_path: str) -> bool:
        try:
            import sqlite3

            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute(
                "SELECT 1 FROM sqlite_master "
                "WHERE type='table' AND name='asset_1'"
            )
            if cur.fetchone() is None:
                return False

            cur.execute("SELECT 1 FROM asset_1 LIMIT 1")
            return cur.fetchone() is not None
        except Exception:
            return False
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def _load(self) -> dict:
        if not os.path.exists(self.data_file):
            return {"status": "MISSING"}

        with open(self.data_file, "r") as f:
            data = json.load(f)

        # Machine binding check
        if data.get("machine_id") != self._machine_id():
            return {"status": "LOCKED"}

        # Expiry check
        if "expires_at" not in data:
            return {"status": "LOCKED"}

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

    def _get_app_data_path(self, app_name):
        return os.path.join(
            os.getenv("APPDATA", os.getcwd()),
            app_name
        )

    def _migrate_legacy(self, legacy_app_name):
        if not legacy_app_name:
            return

        if isinstance(legacy_app_name, (list, tuple, set)):
            for name in legacy_app_name:
                if self._try_migrate_legacy(name):
                    return
            return

        self._try_migrate_legacy(legacy_app_name)

    def _try_migrate_legacy(self, legacy_app_name) -> bool:
        legacy_base = self._get_app_data_path(legacy_app_name)
        legacy_file = os.path.join(legacy_base, "license.dat")

        if os.path.exists(legacy_file):
            os.makedirs(self.base_path, exist_ok=True)
            shutil.copy2(legacy_file, self.data_file)
            return True

        return False
