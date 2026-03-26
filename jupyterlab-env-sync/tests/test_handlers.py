import json

import pytest


async def test_set_and_get_var(jp_fetch):
    # Set a variable
    response = await jp_fetch(
        'jupyterlab-env-sync', 'env', 'TEST_KEY',
        method='PUT',
        body=json.dumps({'extension_id': 'test-ext', 'value': 'hello'}),
    )
    assert response.code == 200
    body = json.loads(response.body)
    assert body['value'] == 'hello'
    assert body['set_by'] == 'test-ext'

    # Get all
    response = await jp_fetch('jupyterlab-env-sync', 'env')
    assert response.code == 200
    data = json.loads(response.body)
    assert 'TEST_KEY' in data
    assert data['TEST_KEY']['value'] == 'hello'


async def test_get_by_extension(jp_fetch):
    await jp_fetch(
        'jupyterlab-env-sync', 'env', 'EXT_KEY',
        method='PUT',
        body=json.dumps({'extension_id': 'my-ext', 'value': 'val'}),
    )
    response = await jp_fetch(
        'jupyterlab-env-sync', 'env',
        params={'extension_id': 'my-ext'},
    )
    assert response.code == 200
    data = json.loads(response.body)
    assert 'EXT_KEY' in data


async def test_reset_var(jp_fetch):
    await jp_fetch(
        'jupyterlab-env-sync', 'env', 'DEL_KEY',
        method='PUT',
        body=json.dumps({'extension_id': 'ext-a', 'value': 'v'}),
    )
    response = await jp_fetch(
        'jupyterlab-env-sync', 'env', 'DEL_KEY',
        method='DELETE',
        body=json.dumps({'extension_id': 'ext-a'}),
        allow_nonstandard_methods=True,
    )
    assert response.code == 200

    response = await jp_fetch('jupyterlab-env-sync', 'env')
    data = json.loads(response.body)
    assert 'DEL_KEY' not in data


async def test_reset_all_by_extension(jp_fetch):
    await jp_fetch(
        'jupyterlab-env-sync', 'env', 'K1',
        method='PUT',
        body=json.dumps({'extension_id': 'clean-ext', 'value': '1'}),
    )
    await jp_fetch(
        'jupyterlab-env-sync', 'env', 'K2',
        method='PUT',
        body=json.dumps({'extension_id': 'clean-ext', 'value': '2'}),
    )
    response = await jp_fetch(
        'jupyterlab-env-sync', 'env', 'extension', 'clean-ext',
        method='DELETE',
    )
    assert response.code == 200
    body = json.loads(response.body)
    assert sorted(body['reset_keys']) == ['K1', 'K2']
