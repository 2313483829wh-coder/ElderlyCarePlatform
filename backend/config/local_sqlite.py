import os
import shutil
import sqlite3
from pathlib import Path


def _is_readable_sqlite(path: Path) -> bool:
    if not path.exists() or path.stat().st_size <= 0:
        return False
    try:
        conn = sqlite3.connect(path)
        try:
            conn.execute('SELECT name FROM sqlite_master LIMIT 1')
            return True
        finally:
            conn.close()
    except sqlite3.Error:
        return False


def _candidate_paths(base_dir: Path) -> list[Path]:
    temp_path = Path(os.environ.get('TEMP', '')) / 'elderlycare-db-test.sqlite3'
    candidates = [temp_path, base_dir / 'db.sqlite3']
    candidates.extend(sorted(base_dir.glob('db.sqlite3.bak-*'), key=lambda p: p.stat().st_mtime, reverse=True))
    return [p for p in candidates if p.exists()]


def resolve_local_sqlite_path(base_dir: Path) -> Path:
    preferred_roots = [
        Path(os.environ.get('TEMP', '')) / 'ElderlyCarePlatform',
        Path(os.environ.get('LOCALAPPDATA', '')) / 'ElderlyCarePlatform',
        base_dir / '.localdb',
    ]

    local_root = None
    for root in preferred_roots:
        if not str(root):
            continue
        try:
            root.mkdir(parents=True, exist_ok=True)
            local_root = root
            break
        except OSError:
            continue

    if local_root is None:
        local_root = base_dir

    local_db = local_root / 'local-dev.sqlite3'

    if _is_readable_sqlite(local_db):
        return local_db

    for candidate in _candidate_paths(base_dir):
        if _is_readable_sqlite(candidate):
            shutil.copy2(candidate, local_db)
            return local_db

    return local_db
