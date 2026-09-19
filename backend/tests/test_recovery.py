from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from domain.recovery_token import RecoveryToken
from domain.user import User
from tests.conftest import RepositoriesContainer


class TestRecoveryFunctional:
    """Функциональные тесты восстановления пароля через временные токены (основной и альтернативный потоки)."""

    # -----------------------------------------------------------------------
    # Основной поток (Happy Path)
    # -----------------------------------------------------------------------

    def test_full_password_recovery_flow_success(
        self,
        client: TestClient,
        student_user: User,
    ) -> None:
        """Основной поток: полный успешный цикл восстановления пароля по токену."""
        # 1. Запрос токена восстановления
        request_resp = client.post(
            "/api/recovery",
            json={"email": student_user.email},
        )
        assert request_resp.status_code == 201
        data = request_resp.json()
        assert "token" in data
        assert data["user_id"] == str(student_user.id)
        assert data["is_expired"] is False
        token = data["token"]

        # 2. Проверка валидности токена
        val_resp = client.get(f"/api/recovery/{token}")
        assert val_resp.status_code == 200
        assert val_resp.json()["token"] == token
        assert val_resp.json()["is_expired"] is False

        # 3. Сброс пароля на новый
        reset_resp = client.post(
            "/api/recovery/reset-password",
            json={"token": token, "new_password": "recoveredPassword123"},
        )
        assert reset_resp.status_code == 200
        assert "успешно" in reset_resp.json().get("message", "")

        # 4. Проверка: старый пароль не подходит
        old_login = client.post(
            "/api/auth/login",
            json={"email": student_user.email, "password": "password123"},
        )
        assert old_login.status_code == 401

        # 5. Проверка: новый пароль работает
        new_login = client.post(
            "/api/auth/login",
            json={"email": student_user.email, "password": "recoveredPassword123"},
        )
        assert new_login.status_code == 200

        # 6. Проверка одноразовости токена: повторное использование невозможно
        second_val = client.get(f"/api/recovery/{token}")
        assert second_val.status_code == 404

    # -----------------------------------------------------------------------
    # Альтернативные потоки (Alternative Flows & Errors)
    # -----------------------------------------------------------------------

    def test_request_recovery_nonexistent_email(
        self,
        client: TestClient,
    ) -> None:
        """Альтернативный поток: запрос токена для неизвестного email -> 404 UserNotFound."""
        response = client.post(
            "/api/recovery",
            json={"email": "unknown.user@edu.ru"},
        )
        assert response.status_code == 404
        assert "не найден" in response.json().get("detail", "")

    def test_request_recovery_invalid_email_format(
        self,
        client: TestClient,
    ) -> None:
        """Альтернативный поток: некорректный формат email -> 422."""
        response = client.post(
            "/api/recovery",
            json={"email": "invalid-email-format"},
        )
        assert response.status_code == 422

    def test_validate_nonexistent_token(
        self,
        client: TestClient,
    ) -> None:
        """Альтернативный поток: проверка несуществующего токена -> 404 RecoveryTokenNotFound."""
        response = client.get("/api/recovery/nonexistent-token-12345")
        assert response.status_code == 404
        assert "не найден" in response.json().get("detail", "")

    def test_validate_expired_token(
        self,
        client: TestClient,
        student_user: User,
        repos: RepositoriesContainer,
    ) -> None:
        """Альтернативный поток: проверка просроченного токена -> 400 RecoveryTokenExpired."""
        expired_token = RecoveryToken(
            user_id=student_user.id,
            token="expired-token-xyz",
            expires_at=datetime.now(UTC) - timedelta(minutes=1),
        )
        repos.recovery_repo.save(expired_token)

        response = client.get("/api/recovery/expired-token-xyz")
        assert response.status_code == 400
        assert "истек" in response.json().get("detail", "")

    def test_reset_password_nonexistent_token(
        self,
        client: TestClient,
    ) -> None:
        """Альтернативный поток: сброс пароля с несуществующим токеном -> 404."""
        response = client.post(
            "/api/recovery/reset-password",
            json={"token": "invalid-token", "new_password": "newStrongPassword123"},
        )
        assert response.status_code == 404

    def test_reset_password_weak_new_password(
        self,
        client: TestClient,
        student_user: User,
        repos: RepositoriesContainer,
    ) -> None:
        """Альтернативный поток: новый пароль при сбросе короче 6 символов -> 422/400."""
        token_obj = RecoveryToken(
            user_id=student_user.id,
            token="valid-token-for-weak-pass",
            expires_at=datetime.now(UTC) + timedelta(minutes=15),
        )
        repos.recovery_repo.save(token_obj)

        response = client.post(
            "/api/recovery/reset-password",
            json={"token": "valid-token-for-weak-pass", "new_password": "123"},
        )
        assert response.status_code in (400, 422)
