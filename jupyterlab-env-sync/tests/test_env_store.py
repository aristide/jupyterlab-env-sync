import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from importlib import import_module

_mod = import_module('jupyterlab-env-sync.env_store')
EnvStore = _mod.EnvStore


@pytest.fixture
def store(tmp_path):
    path = str(tmp_path / 'env_overrides.json')
    return EnvStore(path)


class TestSetVar:
    def test_set_var_creates_entry(self, store):
        entry = store.set_var('ext-a', 'FOO', 'bar')
        assert entry['value'] == 'bar'
        assert entry['set_by'] == 'ext-a'
        assert entry['spawner_value'] is None
        assert os.environ['FOO'] == 'bar'

    def test_set_var_captures_spawner_value(self, store):
        os.environ['EXISTING'] = 'original'
        try:
            entry = store.set_var('ext-a', 'EXISTING', 'override')
            assert entry['spawner_value'] == 'original'
            assert entry['value'] == 'override'
            assert os.environ['EXISTING'] == 'override'
        finally:
            os.environ.pop('EXISTING', None)

    def test_set_var_preserves_spawner_on_overwrite(self, store):
        os.environ['KEY1'] = 'spawner_val'
        try:
            store.set_var('ext-a', 'KEY1', 'val1')
            store.set_var('ext-b', 'KEY1', 'val2')
            data = store.get_all()
            assert data['KEY1']['spawner_value'] == 'spawner_val'
            assert data['KEY1']['set_by'] == 'ext-b'
            assert data['KEY1']['value'] == 'val2'
        finally:
            os.environ.pop('KEY1', None)


class TestResetVar:
    def test_reset_var_restores_spawner(self, store):
        os.environ['RESET_ME'] = 'spawner'
        try:
            store.set_var('ext-a', 'RESET_ME', 'override')
            ok = store.reset_var('ext-a', 'RESET_ME')
            assert ok is True
            assert os.environ['RESET_ME'] == 'spawner'
            assert 'RESET_ME' not in store.get_all()
        finally:
            os.environ.pop('RESET_ME', None)

    def test_reset_var_deletes_when_no_spawner(self, store):
        os.environ.pop('NO_SPAWN', None)
        store.set_var('ext-a', 'NO_SPAWN', 'val')
        ok = store.reset_var('ext-a', 'NO_SPAWN')
        assert ok is True
        assert 'NO_SPAWN' not in os.environ

    def test_reset_var_rejects_non_owner(self, store):
        store.set_var('ext-a', 'OWNED', 'val')
        ok = store.reset_var('ext-b', 'OWNED')
        assert ok is False
        assert store.get_all()['OWNED']['value'] == 'val'
        os.environ.pop('OWNED', None)

    def test_reset_var_with_force(self, store):
        store.set_var('ext-a', 'FORCED', 'val')
        ok = store.reset_var('ext-b', 'FORCED', force=True)
        assert ok is True
        assert 'FORCED' not in store.get_all()
        os.environ.pop('FORCED', None)

    def test_reset_nonexistent_key(self, store):
        ok = store.reset_var('ext-a', 'NOPE')
        assert ok is False


class TestResetAllByExtension:
    def test_resets_only_own_keys(self, store):
        store.set_var('ext-a', 'A1', 'v1')
        store.set_var('ext-a', 'A2', 'v2')
        store.set_var('ext-b', 'B1', 'v3')

        keys = store.reset_all_by_extension('ext-a')
        assert sorted(keys) == ['A1', 'A2']
        data = store.get_all()
        assert 'A1' not in data
        assert 'A2' not in data
        assert 'B1' in data

        os.environ.pop('A1', None)
        os.environ.pop('A2', None)
        os.environ.pop('B1', None)


class TestGetByExtension:
    def test_filters_by_extension(self, store):
        store.set_var('ext-a', 'X', '1')
        store.set_var('ext-b', 'Y', '2')

        result = store.get_by_extension('ext-a')
        assert result == {'X': '1'}

        os.environ.pop('X', None)
        os.environ.pop('Y', None)
