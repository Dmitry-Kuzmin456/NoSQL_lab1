from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


class TestHealthFunctional:
    """Функциональные тесты эндпоинтов проверки жизнеспособности сервиса."""

    def test_app_health_check_success(self, client: TestClient) -> None:
        """Основной поток: общий статус доступности приложения -> 200 OK."""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_riak_health_check_success(self, client: TestClient) -> None:
        """Основной поток: проверка доступности Riak KV при успешном ping -> 200 OK."""
        mock_client = MagicMock()
        mock_client.ping.return_value = True

        with patch(
            "infrastructure.http.health.controller.get_riak_client",
            return_value=mock_client,
        ):
            response = client.get("/api/health/riak")
            assert response.status_code == 200
            data = response.json()
            assert data["riak"] == "ok"
            assert data["status_code"] == 200

    def test_riak_health_check_unreachable(self, client: TestClient) -> None:
        """Альтернативный поток: Riak KV недоступен (ping вернул False) -> 503 в теле ответа."""
        mock_client = MagicMock()
        mock_client.ping.return_value = False

        with patch(
            "infrastructure.http.health.controller.get_riak_client",
            return_value=mock_client,
        ):
            response = client.get("/api/health/riak")
            assert response.status_code == 200
            data = response.json()
            assert data["riak"] == "unreachable"
            assert data["status_code"] == 503
