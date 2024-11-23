from __future__ import annotations


def test_home_page_status_code(client):
    response = client.get("/")
    assert response.status_code == 302
