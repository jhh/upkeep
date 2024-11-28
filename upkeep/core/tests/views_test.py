def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 302
    location = response["Location"]
    assert location == "/areas/"
