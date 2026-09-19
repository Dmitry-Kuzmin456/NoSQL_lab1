from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
from fastapi.testclient import TestClient

from domain.session import Session
from domain.user import User, UserRole
from tests.conftest import RepositoriesContainer


class TestAuthFunctional:
    """Функциональные тесты аутентификации и авторизации (основной и альтернативный потоки)."""

    # -----------------------------------------------------------------------
    # Основной поток (Happy Path)
    # -----------------------------------------------------------------------

    def test_login_success_student(
        self,
        client: TestClient,
        student_user: User,
    ) -> None:
        """Основной поток: успешный вход студента по email и паролю."""
        response = client.post(
            "/api/auth/login",
            json={"email": student_user.email, "password": "password123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(student_user.id)
        assert data["email"] == student_user.email
        assert data["role"] == UserRole.STUDENT.value

        # Проверка установки auth-cookies
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies

    def test_login_success_teacher(
        self,
        client: TestClient,
        teacher_user: User,
    ) -> None:
        """Основной поток: успешный вход преподавателя."""
        response = client.post(
            "/api/auth/login",
            json={"email": teacher_user.email, "password": "password123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(teacher_user.id)
        assert data["role"] == UserRole.TEACHER.value

    def test_login_success_admin(
        self,
        client: TestClient,
        admin_user: User,
    ) -> None:
        """Основной поток: успешный вход администратора."""
        response = client.post(
            "/api/auth/login",
            json={"email": admin_user.email, "password": "adminPassword123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(admin_user.id)
        assert data["role"] == UserRole.ADMIN.value

    def test_login_case_insensitive_email(
        self,
        client: TestClient,
        student_user: User,
    ) -> None:
        """Основной поток: регистронезависимый вход по email."""
        response = client.post(
            "/api/auth/login",
            json={"email": student_user.email.upper(), "password": "password123"},
        )
        assert response.status_code == 200
        assert response.json()["id"] == str(student_user.id)

    def test_refresh_token_success(
        self,
        client: TestClient,
        student_user: User,
        repos: RepositoriesContainer,
    ) -> None:
        """Основной поток: успешное обновление токенов через refresh_token cookie."""
        login_resp = client.post(
            "/api/auth/login",
            json={"email": student_user.email, "password": "password123"},
        )
        old_refresh_token = login_resp.cookies["refresh_token"]

        # Обновление токена
        client.cookies.set("refresh_token", old_refresh_token)
        refresh_resp = client.post("/api/auth/refresh")

        assert refresh_resp.status_code == 200
        data = refresh_resp.json()
        assert data["id"] == str(student_user.id)

        new_refresh_token = refresh_resp.cookies.get("refresh_token")
        assert new_refresh_token is not None
        assert new_refresh_token != old_refresh_token
        # Старая сессия должна быть удалена
        assert repos.session_repo.get_by_refresh_token(old_refresh_token) is None
        # Новая сессия должна существовать
        assert repos.session_repo.get_by_refresh_token(new_refresh_token) is not None

    def test_logout_success_with_refresh_cookie(
        self,
        client: TestClient,
        student_user: User,
        student_auth_headers: dict[str, str],
        repos: RepositoriesContainer,
    ) -> None:
        """Основной поток: выход из системы с отзывом сессии."""
        login_resp = client.post(
            "/api/auth/login",
            json={"email": student_user.email, "password": "password123"},
        )
        refresh_token = login_resp.cookies["refresh_token"]

        client.cookies.set("refresh_token", refresh_token)
        logout_resp = client.post(
            "/api/auth/logout",
            headers=student_auth_headers,
        )
        assert logout_resp.status_code == 204
        assert repos.session_repo.get_by_refresh_token(refresh_token) is None

    def test_logout_all_me_success(
        self,
        client: TestClient,
        student_user: User,
        student_auth_headers: dict[str, str],
        repos: RepositoriesContainer,
    ) -> None:
        """Основной поток: завершение всех сессий текущего пользователя."""
        # Создаем 2 сессии
        client.post(
            "/api/auth/login",
            json={"email": student_user.email, "password": "password123"},
        )
        client.post(
            "/api/auth/login",
            json={"email": student_user.email, "password": "password123"},
        )
        assert len(repos.session_repo.list_by_user_id(student_user.id)) >= 2

        resp = client.post(
            "/api/auth/logout-all/me",
            headers=student_auth_headers,
        )
        assert resp.status_code == 204
        assert len(repos.session_repo.list_by_user_id(student_user.id)) == 0

    def test_logout_all_by_user_id_admin_success(
        self,
        client: TestClient,
        student_user: User,
        admin_auth_headers: dict[str, str],
        repos: RepositoriesContainer,
    ) -> None:
        """Основной поток: администратор отзывает все сессии указанного пользователя."""
        client.post(
            "/api/auth/login",
            json={"email": student_user.email, "password": "password123"},
        )
        assert len(repos.session_repo.list_by_user_id(student_user.id)) >= 1

        resp = client.post(
            f"/api/auth/logout-all/{student_user.id}",
            headers=admin_auth_headers,
        )
        assert resp.status_code == 204
        assert len(repos.session_repo.list_by_user_id(student_user.id)) == 0

    def test_auth_via_access_token_cookie(
        self,
        client: TestClient,
        student_user: User,
    ) -> None:
        """Основной поток: аутентификация через cookie access_token."""
        login_resp = client.post(
            "/api/auth/login",
            json={"email": student_user.email, "password": "password123"},
        )
        access_token = login_resp.cookies["access_token"]

        # Очищаем заголовки и проверяем доступ к /users/me чисто по cookie
        client.cookies.set("access_token", access_token)
        me_resp = client.get("/api/users/me")
        assert me_resp.status_code == 200
        assert me_resp.json()["id"] == str(student_user.id)

    # -----------------------------------------------------------------------
    # Альтернативные потоки (Alternative Flows & Errors)
    # -----------------------------------------------------------------------

    def test_login_invalid_password(
        self,
        client: TestClient,
        student_user: User,
    ) -> None:
        """Альтернативный поток: неверный пароль -> 401 Unauthorized."""
        response = client.post(
            "/api/auth/login",
            json={"email": student_user.email, "password": "wrongpassword"},
        )
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_login_nonexistent_email(
        self,
        client: TestClient,
    ) -> None:
        """Альтернативный поток: несуществующий email -> 401 Unauthorized."""
        response = client.post(
            "/api/auth/login",
            json={"email": "nobody@example.com", "password": "password123"},
        )
        assert response.status_code == 401

    def test_login_invalid_email_format(
        self,
        client: TestClient,
    ) -> None:
        """Альтернативный поток: некорректный формат email -> 422 Validation Error."""
        response = client.post(
            "/api/auth/login",
            json={"email": "not-an-email", "password": "password123"},
        )
        assert response.status_code == 422

    def test_refresh_token_missing_cookie(
        self,
        client: TestClient,
    ) -> None:
        """Альтернативный поток: запрос refresh без cookie -> 422 Unprocessable Entity."""
        client.cookies.clear()
        response = client.post("/api/auth/refresh")
        assert response.status_code == 422

    def test_refresh_token_nonexistent(
        self,
        client: TestClient,
    ) -> None:
        """Альтернативный поток: неизвестный refresh token -> 404 SessionNotFound."""
        client.cookies.set("refresh_token", "nonexistent-refresh-token")
        response = client.post("/api/auth/refresh")
        assert response.status_code == 404

    def test_refresh_token_expired(
        self,
        client: TestClient,
        student_user: User,
        repos: RepositoriesContainer,
    ) -> None:
        """Альтернативный поток: истекший срок refresh токена -> 401 SessionExpired."""
        expired_session = Session(
            user_id=student_user.id,
            refresh_token="expired-token-123",
            expires_at=datetime.now(UTC) - timedelta(days=1),
        )
        repos.session_repo.save(expired_session)

        client.cookies.set("refresh_token", "expired-token-123")
        response = client.post("/api/auth/refresh")
        assert response.status_code == 401

    def test_logout_unauthenticated(
        self,
        client: TestClient,
    ) -> None:
        """Альтернативный поток: выход неаутентифицированного пользователя -> 401."""
        client.cookies.clear()
        response = client.post("/api/auth/logout")
        assert response.status_code == 401

    def test_logout_all_me_unauthenticated(
        self,
        client: TestClient,
    ) -> None:
        """Альтернативный поток: logout-all/me без токена -> 401 Unauthorized."""
        response = client.post("/api/auth/logout-all/me")
        assert response.status_code == 401

    def test_logout_all_by_user_id_forbidden_for_student(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
    ) -> None:
        """Альтернативный поток: студент пытается вызвать админский logout-all -> 403 Forbidden."""
        response = client.post(
            f"/api/auth/logout-all/{uuid4()}",
            headers=student_auth_headers,
        )
        assert response.status_code == 403

    def test_logout_all_by_user_id_forbidden_for_teacher(
        self,
        client: TestClient,
        teacher_auth_headers: dict[str, str],
    ) -> None:
        """Альтернативный поток: преподаватель пытается вызвать админский logout-all -> 403 Forbidden."""
        response = client.post(
            f"/api/auth/logout-all/{uuid4()}",
            headers=teacher_auth_headers,
        )
        assert response.status_code == 403

    def test_authentication_invalid_bearer_token(
        self,
        client: TestClient,
    ) -> None:
        """Альтернативный поток: доступ с поддельным/некорректным токеном -> 401."""
        response = client.get(
            "/api/users/me",
            headers={"Authorization": "Bearer invalid.jwt.token"},
        )
        assert response.status_code == 401

    def test_authentication_expired_bearer_token(
        self,
        client: TestClient,
        student_user: User,
    ) -> None:
        """Альтернативный поток: доступ с истекшим access токеном -> 401."""
        from infrastructure.environment.settings import settings

        expired_payload = {
            "user_id": str(student_user.id),
            "role": student_user.role.value,
            "exp": int((datetime.now(UTC) - timedelta(minutes=5)).timestamp()),
        }
        expired_token = jwt.encode(
            expired_payload,
            settings.auth.jwt_secret_key,
            algorithm=settings.auth.jwt_algorithm,
        )

        response = client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401
