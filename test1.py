import pytest
from fastapi.testclient import TestClient
from main1 import app, WalletQuery


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def test_post_wallet(client):

    class DummyClient:
        def get_account(self, address):
            return {'balance': 10_000_000}

        def get_account_resource(self, address):
            return {'free_net_remaining': 1000, 'energy_remaining': 2000}

    from main1 import Tron
    Tron = DummyClient

    response = client.post("/wallet", json={"address": "TXYZ12345TEST"})

    assert response.status_code == 200
    data = response.json()

    assert data["balance"] == 10.0
    assert data["bandwidth"] == 1000
    assert data["energy"] == 2000
