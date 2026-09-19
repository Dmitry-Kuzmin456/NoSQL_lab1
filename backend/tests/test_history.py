from fastapi.testclient import TestClient

from domain.history import OperationEvent, OperationType
from domain.product import Product
from domain.user import User
from tests.conftest import RepositoriesContainer


class TestHistoryFunctional:
    """Функциональные тесты аудита и истории операций пользователя (основной и альтернативный потоки)."""

    # -----------------------------------------------------------------------
    # Основной поток (Happy Path)
    # -----------------------------------------------------------------------

    def test_history_records_events_and_get_me(
        self,
        client: TestClient,
        student_user: User,
        student_auth_headers: dict[str, str],
        sample_product: Product,
    ) -> None:
        """Основной поток: действия пользователя фиксируются в истории и доступны для чтения."""
        # Выполняем действия
        client.post(
            "/api/users/me/favourites",
            headers=student_auth_headers,
            json={"product_id": str(sample_product.id)},
        )
        client.patch(
            f"/api/users/me/cart/items/{sample_product.id}",
            headers=student_auth_headers,
            json={"quantity": 2},
        )

        # Запрашиваем историю
        response = client.get("/api/users/me/history", headers=student_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == str(student_user.id)
        events = data["events"]
        assert len(events) >= 2

        actions = [e["action"] for e in events]
        assert OperationType.ADD_FAVOURITE.value in actions
        assert OperationType.UPDATE_CART_ITEM.value in actions

    def test_history_pagination(
        self,
        client: TestClient,
        student_user: User,
        student_auth_headers: dict[str, str],
        repos: RepositoriesContainer,
    ) -> None:
        """Основной поток: пагинация по событиям истории (offset и limit)."""
        # Наполняем историю событиями
        for i in range(5):
            repos.history_repo.add_event(
                OperationEvent(
                    user_id=student_user.id,
                    action=OperationType.ADD_CART_ITEM,
                    details={"index": i},
                )
            )

        # Запрашиваем первую страницу из 2 элементов
        page1 = client.get(
            "/api/users/me/history",
            headers=student_auth_headers,
            params={"offset": 0, "limit": 2},
        )
        assert page1.status_code == 200
        assert len(page1.json()["events"]) == 2

        # Вторая страница
        page2 = client.get(
            "/api/users/me/history",
            headers=student_auth_headers,
            params={"offset": 2, "limit": 2},
        )
        assert page2.status_code == 200
        assert len(page2.json()["events"]) == 2

    def test_clear_my_history_success(
        self,
        client: TestClient,
        student_user: User,
        student_auth_headers: dict[str, str],
        repos: RepositoriesContainer,
    ) -> None:
        """Основной поток: очистка истории действий текущего пользователя."""
        repos.history_repo.add_event(
            OperationEvent(user_id=student_user.id, action=OperationType.UPDATE_PROFILE)
        )

        clear_resp = client.delete(
            "/api/users/me/history", headers=student_auth_headers
        )
        assert clear_resp.status_code == 204

        # История должна быть пуста
        get_resp = client.get("/api/users/me/history", headers=student_auth_headers)
        assert len(get_resp.json()["events"]) == 0

    def test_admin_manage_user_history_success(
        self,
        client: TestClient,
        student_user: User,
        admin_auth_headers: dict[str, str],
        repos: RepositoriesContainer,
    ) -> None:
        """Основной поток: администратор просматривает и очищает историю пользователя по ID."""
        repos.history_repo.add_event(
            OperationEvent(user_id=student_user.id, action=OperationType.USER_REGISTER)
        )

        # Админ читает историю студента
        get_resp = client.get(
            f"/api/users/{student_user.id}/history",
            headers=admin_auth_headers,
        )
        assert get_resp.status_code == 200
        assert len(get_resp.json()["events"]) >= 1

        # Админ очищает историю студента
        del_resp = client.delete(
            f"/api/users/{student_user.id}/history",
            headers=admin_auth_headers,
        )
        assert del_resp.status_code == 204

    # -----------------------------------------------------------------------
    # Альтернативные потоки (Alternative Flows & Errors)
    # -----------------------------------------------------------------------

    def test_get_history_me_unauthenticated(
        self,
        client: TestClient,
    ) -> None:
        """Альтернативный поток: запрос истории без авторизации -> 401."""
        response = client.get("/api/users/me/history")
        assert response.status_code == 401

    def test_get_history_by_user_id_forbidden_for_student(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
        teacher_user: User,
    ) -> None:
        """Альтернативный поток: студент пытается посмотреть историю другого пользователя -> 403."""
        response = client.get(
            f"/api/users/{teacher_user.id}/history",
            headers=student_auth_headers,
        )
        assert response.status_code == 403

    def test_clear_history_me_unauthenticated(
        self,
        client: TestClient,
    ) -> None:
        """Альтернативный поток: очистка истории без авторизации -> 401."""
        response = client.delete("/api/users/me/history")
        assert response.status_code == 401

    def test_clear_history_by_user_id_forbidden_for_student(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
        teacher_user: User,
    ) -> None:
        """Альтернативный поток: студент пытается очистить чужую историю -> 403."""
        response = client.delete(
            f"/api/users/{teacher_user.id}/history",
            headers=student_auth_headers,
        )
        assert response.status_code == 403

    def test_history_invalid_pagination(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
    ) -> None:
        """Альтернативный поток: отрицательный offset или limit > 100 -> 422."""
        assert (
            client.get(
                "/api/users/me/history",
                headers=student_auth_headers,
                params={"offset": -1},
            ).status_code
            == 422
        )
        assert (
            client.get(
                "/api/users/me/history",
                headers=student_auth_headers,
                params={"limit": 0},
            ).status_code
            == 422
        )
        assert (
            client.get(
                "/api/users/me/history",
                headers=student_auth_headers,
                params={"limit": 500},
            ).status_code
            == 422
        )
