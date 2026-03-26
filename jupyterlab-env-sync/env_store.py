import json
import os
import tempfile
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class EnvStore:
    """Manages environment variable overrides via a JSON file and os.environ."""

    def __init__(self, store_path):
        self._store_path = store_path
        os.makedirs(os.path.dirname(store_path), exist_ok=True)

    def _load(self):
        try:
            with open(self._store_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save(self, data):
        dir_name = os.path.dirname(self._store_path)
        fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix='.tmp')
        try:
            with os.fdopen(fd, 'w') as f:
                json.dump(data, f, indent=2)
            os.rename(tmp_path, self._store_path)
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

    def get_all(self):
        return self._load()

    def get_by_extension(self, extension_id):
        data = self._load()
        return {
            k: v['value']
            for k, v in data.items()
            if v.get('set_by') == extension_id
        }

    def set_var(self, extension_id, key, value):
        data = self._load()
        existing = data.get(key)

        if existing and existing.get('set_by') != extension_id:
            logger.warning(
                'Extension %s is overwriting key %s previously set by %s',
                extension_id, key, existing['set_by']
            )

        spawner_value = (
            existing['spawner_value']
            if existing
            else os.environ.get(key)
        )

        entry = {
            'value': value,
            'spawner_value': spawner_value,
            'set_by': extension_id,
            'set_at': datetime.now(timezone.utc).isoformat(),
        }
        data[key] = entry
        self._save(data)
        os.environ[key] = value
        return entry

    def reset_var(self, extension_id, key, force=False):
        data = self._load()
        entry = data.get(key)
        if entry is None:
            return False

        if entry['set_by'] != extension_id and not force:
            logger.warning(
                'Extension %s cannot reset key %s owned by %s without force=true',
                extension_id, key, entry['set_by']
            )
            return False

        spawner_value = entry.get('spawner_value')
        if spawner_value is not None:
            os.environ[key] = spawner_value
        else:
            os.environ.pop(key, None)

        del data[key]
        self._save(data)
        return True

    def reset_all_by_extension(self, extension_id):
        data = self._load()
        keys_to_reset = [
            k for k, v in data.items()
            if v.get('set_by') == extension_id
        ]
        for key in keys_to_reset:
            entry = data[key]
            spawner_value = entry.get('spawner_value')
            if spawner_value is not None:
                os.environ[key] = spawner_value
            else:
                os.environ.pop(key, None)
            del data[key]

        self._save(data)
        return keys_to_reset
