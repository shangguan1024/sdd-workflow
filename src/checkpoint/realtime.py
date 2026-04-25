"""
RealTime Sync
实时 Checkpoint 同步 — 真正的状态采集与定时持久化
"""

import json
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Callable


class RealTimeSync:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self._sync_threads: dict[str, threading.Thread] = {}
        self._sync_enabled: dict[str, bool] = {}
        self._sync_interval = 30
        self._state_collectors: dict[str, Callable] = {}
        self._last_sync_times: dict[str, str] = {}
        self._sync_stats: dict[str, dict] = {}

    def enable(self, feature_name: str, state_collector: Callable = None):
        if feature_name in self._sync_threads and self._sync_threads[feature_name].is_alive():
            return

        self._sync_enabled[feature_name] = True
        if state_collector:
            self._state_collectors[feature_name] = state_collector

        self._sync_stats.setdefault(feature_name, {
            "sync_count": 0,
            "last_sync": None,
            "errors": [],
            "enabled_at": datetime.now().isoformat(),
        })

        thread = threading.Thread(
            target=self._sync_worker,
            args=(feature_name,),
            daemon=True,
        )
        self._sync_threads[feature_name] = thread
        thread.start()

    def disable(self, feature_name: str):
        self._sync_enabled[feature_name] = False

        if feature_name in self._sync_threads:
            self._sync_threads[feature_name].join(timeout=2)
            del self._sync_threads[feature_name]

    def set_collector(self, feature_name: str, collector: Callable):
        self._state_collectors[feature_name] = collector

    def sync(self, feature_name: str) -> bool:
        feature_dir = self.project_root / "docs" / "features" / feature_name
        if not feature_dir.exists():
            return False

        sync_dir = feature_dir / ".sdd" / "sync"
        sync_dir.mkdir(parents=True, exist_ok=True)

        sync_data = {
            "timestamp": datetime.now().isoformat(),
            "feature_name": feature_name,
            "project_root": str(self.project_root),
        }

        collector = self._state_collectors.get(feature_name)
        if collector:
            try:
                collected = collector()
                if isinstance(collected, dict):
                    sync_data["state"] = collected
            except Exception as e:
                self._sync_stats[feature_name]["errors"].append({
                    "time": datetime.now().isoformat(),
                    "error": str(e),
                })

        sync_data["sync_stats"] = self._sync_stats.get(feature_name, {})

        try:
            sync_file = sync_dir / "realtime_snapshot.json"
            backup_file = sync_dir / "realtime_snapshot.backup.json"

            if sync_file.exists():
                sync_file.rename(backup_file)

            with open(sync_file, "w", encoding="utf-8") as f:
                json.dump(sync_data, f, indent=2, ensure_ascii=False)

            if backup_file.exists():
                backup_file.unlink()

            self._last_sync_times[feature_name] = sync_data["timestamp"]
            self._sync_stats[feature_name]["sync_count"] += 1
            self._sync_stats[feature_name]["last_sync"] = sync_data["timestamp"]

            return True
        except IOError:
            return False

    def force_sync(self, feature_name: str, state: dict = None) -> bool:
        if state:
            self._state_collectors[feature_name] = lambda: state
        return self.sync(feature_name)

    def get_sync_status(self, feature_name: str) -> dict:
        return {
            "enabled": self._sync_enabled.get(feature_name, False),
            "last_sync": self._last_sync_times.get(feature_name),
            "stats": self._sync_stats.get(feature_name, {}),
            "has_collector": feature_name in self._state_collectors,
        }

    def load_sync_snapshot(self, feature_name: str) -> Optional[dict]:
        sync_file = (
            self.project_root / "docs" / "features" / feature_name
            / ".sdd" / "sync" / "realtime_snapshot.json"
        )
        if not sync_file.exists():
            return None

        try:
            with open(sync_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def is_enabled(self, feature_name: str) -> bool:
        return self._sync_enabled.get(feature_name, False)

    def _sync_worker(self, feature_name: str):
        while self._sync_enabled.get(feature_name, False):
            self.sync(feature_name)
            time.sleep(self._sync_interval)
