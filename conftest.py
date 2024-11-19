from __future__ import annotations

import pytest
from django.test.utils import override_settings


@pytest.fixture(scope="session", autouse=True)
def test_settings():
    with override_settings(**TEST_SETTINGS):
        yield


TEST_SETTINGS = {
    "STATIC_ROOT": None,
    "STORAGES": {
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    },
}
