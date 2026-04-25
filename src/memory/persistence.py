"""
Memory Persistence: save/load conversation memory with versioning and backup.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional


class MemoryPersistence:
    MEMORY_FILE = "conversation_memory.json"
    BACKUP_FILE = "conversation_memory.backup.json"
    HISTORY_DIR = "memory_history"
    MAX_HISTORY = 50

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)

    def memory_dir(self, feature_name: str) -> Path:
        return self.project_root / "docs" / "features" / feature_name / ".sdd"

    def save(self, memory, feature_name: str) -> Path:
        mem_dir = self.memory_dir(feature_name)
        mem_dir.mkdir(parents=True, exist_ok=True)

        memory_path = mem_dir / self.MEMORY_FILE
        backup_path = mem_dir / self.BACKUP_FILE

        if memory_path.exists():
            try:
                memory_path.rename(backup_path)
            except OSError:
                pass

        try:
            snapshot = memory.get_memory_snapshot()
            with open(memory_path, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, indent=2, ensure_ascii=False)

            self._save_to_history(mem_dir, snapshot)

            if backup_path.exists():
                backup_path.unlink()

        except Exception:
            if backup_path.exists():
                backup_path.rename(memory_path)
            raise

        return memory_path

    def load(self, feature_name: str) -> Optional[dict]:
        mem_dir = self.memory_dir(feature_name)
        memory_path = mem_dir / self.MEMORY_FILE

        if not memory_path.exists():
            return None

        try:
            with open(memory_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return self._load_backup(mem_dir)

    def _load_backup(self, mem_dir: Path) -> Optional[dict]:
        backup_path = mem_dir / self.BACKUP_FILE
        if not backup_path.exists():
            return None

        try:
            with open(backup_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def exists(self, feature_name: str) -> bool:
        return (self.memory_dir(feature_name) / self.MEMORY_FILE).exists()

    def list_history(self, feature_name: str) -> list[dict]:
        history_dir = self.memory_dir(feature_name) / self.HISTORY_DIR
        if not history_dir.exists():
            return []

        snapshots = []
        for path in sorted(history_dir.glob("memory_*.json"),
                           key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    snapshots.append(json.load(f))
            except (json.JSONDecodeError, IOError):
                continue

        return snapshots

    def delete(self, feature_name: str) -> bool:
        mem_dir = self.memory_dir(feature_name)
        if not mem_dir.exists():
            return True

        import shutil
        memory_path = mem_dir / self.MEMORY_FILE
        backup_path = mem_dir / self.BACKUP_FILE
        history_dir = mem_dir / self.HISTORY_DIR

        for path in [memory_path, backup_path]:
            if path.exists():
                path.unlink()

        if history_dir.exists():
            shutil.rmtree(history_dir, ignore_errors=True)

        return True

    def _save_to_history(self, mem_dir: Path, snapshot: dict):
        history_dir = mem_dir / self.HISTORY_DIR
        history_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_file = history_dir / f"memory_{timestamp}.json"

        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)

        self._cleanup_history(history_dir)

    def _cleanup_history(self, history_dir: Path):
        files = sorted(history_dir.glob("memory_*.json"),
                       key=lambda p: p.stat().st_mtime, reverse=True)
        for old_file in files[self.MAX_HISTORY:]:
            old_file.unlink()
