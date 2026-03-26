import json

import pytest


async def test_hello_endpoint(jp_fetch):
    response = await jp_fetch("jupyterlab-env-sync", "hello")
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == {"data": "Hello World from jupyterlab-env-sync!"}
