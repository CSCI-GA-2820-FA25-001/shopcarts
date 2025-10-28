"""Tests for POST /shopcarts/<id>/clear endpoint."""

from service.common import status


def _create_cart(client, name="aryaman"):
    resp = client.post(
        "/shopcarts",
        json={"name": name},
        content_type="application/json",
    )
    assert resp.status_code == status.HTTP_201_CREATED
    return resp.get_json()["id"]


def _add_item(client, cart_id, name="apple", quantity=2, unit_price="1.25"):
    resp = client.post(
        f"/shopcarts/{cart_id}/items",
        json={"name": name, "quantity": quantity, "unit_price": unit_price},
        content_type="application/json",
    )
    assert resp.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK)
    return resp.get_json()


def test_clear_nonempty_cart(client):
    cart_id = _create_cart(client)
    _add_item(client, cart_id, "apple", 2, "1.25")
    _add_item(client, cart_id, "banana", 1, "0.99")

    resp = client.post(f"/shopcarts/{cart_id}/clear")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.get_json()

    # After clear, a GET should show 0 items (stay consistent with existing serializer)
    get_resp = client.get(f"/shopcarts/{cart_id}")
    assert get_resp.status_code == status.HTTP_200_OK
    body = get_resp.get_json()
    assert body.get("count", len(body.get("items", []))) == 0


def test_clear_invalid_cart_id(client):
    resp = client.post("/shopcarts/999999/clear")
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    msg = resp.get_json().get("message", "").lower()
    assert "not found" in msg or "does not exist" in msg


def test_clear_already_empty_is_idempotent(client):
    cart_id = _create_cart(client)

    # first clear
    resp1 = client.post(f"/shopcarts/{cart_id}/clear")
    assert resp1.status_code == status.HTTP_200_OK

    # second clear should also be OK (idempotent)
    resp2 = client.post(f"/shopcarts/{cart_id}/clear")
    assert resp2.status_code == status.HTTP_200_OK

    get_resp = client.get(f"/shopcarts/{cart_id}")
    assert get_resp.status_code == status.HTTP_200_OK
    body = get_resp.get_json()
    assert body.get("count", len(body.get("items", []))) == 0
