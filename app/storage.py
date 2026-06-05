from __future__ import annotations

import hashlib
from pathlib import Path

from app.models import StoredFile


class MirrorStore:
    def __init__(self, root: Path) -> None:
        self.root = root

    def _stored_file_for_path(self, path: Path, *, created: bool) -> StoredFile:
        data = path.read_bytes()
        return StoredFile(
            storage_key=path.relative_to(self.root).as_posix(),
            path=path,
            checksum=hashlib.sha256(data).hexdigest(),
            created=created,
            size=len(data),
        )

    def find_existing(self, storage_key_prefix: str) -> StoredFile | None:
        path_prefix = self.root / Path(storage_key_prefix)
        matches: list[Path] = []
        if path_prefix.is_file():
            matches.append(path_prefix)
        if path_prefix.parent.exists():
            matches.extend(candidate for candidate in sorted(path_prefix.parent.glob(f"{path_prefix.name}.*")) if candidate.is_file())
        unique_matches = list(dict.fromkeys(matches))
        if len(unique_matches) > 1:
            preferred_matches = [candidate for candidate in unique_matches if candidate.suffix.lower() in {".pdf", ".zip"}]
            if len(preferred_matches) == 1:
                return self._stored_file_for_path(preferred_matches[0], created=False)
        if len(unique_matches) != 1:
            return None
        return self._stored_file_for_path(unique_matches[0], created=False)

    def delete_matching_except(self, storage_key_prefix: str, keep_storage_key: str) -> None:
        path_prefix = self.root / Path(storage_key_prefix)
        keep_path = self.root / Path(keep_storage_key)
        candidates: list[Path] = []
        if path_prefix.is_file():
            candidates.append(path_prefix)
        if path_prefix.parent.exists():
            candidates.extend(candidate for candidate in sorted(path_prefix.parent.glob(f"{path_prefix.name}.*")) if candidate.is_file())
        for candidate in dict.fromkeys(candidates):
            if candidate != keep_path:
                candidate.unlink(missing_ok=True)

    def write_bytes(self, storage_key: str, data: bytes, *, overwrite: bool = False) -> StoredFile:
        path = self.root / Path(storage_key)
        path.parent.mkdir(parents=True, exist_ok=True)
        created = not path.exists()
        if created or overwrite:
            path.write_bytes(data)
        return self._stored_file_for_path(path, created=created)
