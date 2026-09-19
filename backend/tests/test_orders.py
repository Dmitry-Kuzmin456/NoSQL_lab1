from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from domain.order import OrderStatus
from domain.product import Product
from domain.user import User
from tests.conftest import RepositoriesContainer


class TestOrdersFunctional:
    """Функциональные тесты заказов и изменения статусов (основной и альтернативный потоки)."""

    # -----------------------------------------------------------------------
    # Основной поток (Happy Path)
    # -----------------------------------------------------------------------

    def test_create_order_me_success(
        self,
        client: TestClient,
        student_user: User,
        student_auth_headers: dict[str, str],
        sample_product: Product,
        repos: RepositoriesContainer,
    ) -> None:
        """Основной поток: студент создает заказ, остаток товара уменьшается, счетчик инкрементируется."""
        initial_stock = sample_product.quantity
        order_qty = 2

        response = client.post(
            "/api/users/me/orders",
            headers=student_auth_headers,
            json={"product_id": str(sample_product.id), "quantity": order_qty},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == str(student_user.id)
        assert data["product_id"] == str(sample_product.id)
        assert data["quantity"] == order_qty
        assert data["status"] == OrderStatus.CREATED.value
        assert Decimal(str(data["total_amount"])) == sample_product.price * order_qty

        # Проверяем уменьшение остатка
        updated_product = repos.product_repo.get_by_id(sample_product.id)
        assert updated_product is not None
        assert updated_product.quantity == initial_stock - order_qty

        # Проверяем счетчик заказов пользователя
        assert repos.counter_repo.get_by_user_id(student_user.id) >= 1

    def test_list_and_get_my_orders(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
        sample_product: Product,
    ) -> None:
        """Основной поток: получение списка своих заказов с фильтрацией и получение заказа по ID."""
        # Создаем заказ
        create_resp = client.post(
            "/api/users/me/orders",
            headers=student_auth_headers,
            json={"product_id": str(sample_product.id), "quantity": 1},
        )
        order_id = create_resp.json()["id"]

        # Получаем список
        list_resp = client.get(
            "/api/users/me/orders",
            headers=student_auth_headers,
            params={"status": OrderStatus.CREATED.value},
        )
        assert list_resp.status_code == 200
        items = list_resp.json()["items"]
        assert len(items) >= 1
        assert any(o["id"] == order_id for o in items)

        # Получаем один заказ
        get_resp = client.get(
            f"/api/users/me/orders/{order_id}",
            headers=student_auth_headers,
        )
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == order_id

    def test_cancel_my_order_restores_stock(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
        sample_product: Product,
        repos: RepositoriesContainer,
    ) -> None:
        """Основной поток: отмена созданного заказа переводит его в CANCELLED и возвращает остаток на склад."""
        initial_stock = sample_product.quantity

        create_resp = client.post(
            "/api/users/me/orders",
            headers=student_auth_headers,
            json={"product_id": str(sample_product.id), "quantity": 3},
        )
        order_id = create_resp.json()["id"]
        prod_after_create = repos.product_repo.get_by_id(sample_product.id)
        assert prod_after_create is not None
        assert prod_after_create.quantity == initial_stock - 3

        # Отменяем
        cancel_resp = client.post(
            f"/api/users/me/orders/{order_id}/cancel",
            headers=student_auth_headers,
        )
        assert cancel_resp.status_code == 200
        assert cancel_resp.json()["status"] == OrderStatus.CANCELLED.value

        # Проверяем возврат остатка
        prod_after_cancel = repos.product_repo.get_by_id(sample_product.id)
        assert prod_after_cancel is not None
        assert prod_after_cancel.quantity == initial_stock

    def test_admin_approve_and_reject_order_lifecycle(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
        admin_auth_headers: dict[str, str],
        sample_product: Product,
        repos: RepositoriesContainer,
    ) -> None:
        """Основной поток: подтверждение (approve) и отклонение (reject) заказов администратором."""
        initial_stock = sample_product.quantity

        # 1. Заказ для подтверждения
        resp1 = client.post(
            "/api/users/me/orders",
            headers=student_auth_headers,
            json={"product_id": str(sample_product.id), "quantity": 1},
        )
        order1_id = resp1.json()["id"]

        approve_resp = client.post(
            f"/api/orders/{order1_id}/approve",
            headers=admin_auth_headers,
        )
        assert approve_resp.status_code == 200
        assert approve_resp.json()["status"] == OrderStatus.APPROVED.value

        # 2. Заказ для отклонения (должен вернуть остаток на склад)
        resp2 = client.post(
            "/api/users/me/orders",
            headers=student_auth_headers,
            json={"product_id": str(sample_product.id), "quantity": 2},
        )
        order2_id = resp2.json()["id"]
        prod_after_order2 = repos.product_repo.get_by_id(sample_product.id)
        assert prod_after_order2 is not None
        assert prod_after_order2.quantity == initial_stock - 1 - 2

        reject_resp = client.post(
            f"/api/orders/{order2_id}/reject",
            headers=admin_auth_headers,
        )
        assert reject_resp.status_code == 200
        assert reject_resp.json()["status"] == OrderStatus.REJECTED.value

        # Проверяем, что 2 шт вернулись на склад
        prod_after_reject = repos.product_repo.get_by_id(sample_product.id)
        assert prod_after_reject is not None
        assert prod_after_reject.quantity == initial_stock - 1

    def test_admin_list_orders_and_filter(
        self,
        client: TestClient,
        student_user: User,
        student_auth_headers: dict[str, str],
        admin_auth_headers: dict[str, str],
        sample_product: Product,
    ) -> None:
        """Основной поток: администратор просматривает все заказы с фильтрацией по пользователю и статусу."""
        client.post(
            "/api/users/me/orders",
            headers=student_auth_headers,
            json={"product_id": str(sample_product.id), "quantity": 1},
        )

        resp = client.get(
            "/api/orders",
            headers=admin_auth_headers,
            params={
                "user_id": str(student_user.id),
                "status": OrderStatus.CREATED.value,
            },
        )
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) >= 1
        assert all(o["user_id"] == str(student_user.id) for o in items)

    # -----------------------------------------------------------------------
    # Альтернативные потоки (Alternative Flows & Errors)
    # -----------------------------------------------------------------------

    def test_create_order_insufficient_stock(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
        sample_product: Product,
    ) -> None:
        """Альтернативный поток: создание заказа с количеством больше остатка -> 400 InsufficientStock."""
        response = client.post(
            "/api/users/me/orders",
            headers=student_auth_headers,
            json={
                "product_id": str(sample_product.id),
                "quantity": sample_product.quantity + 999,
            },
        )
        assert response.status_code == 400
        assert "Недостаточно товара на складе" in response.json().get("detail", "")

    def test_create_order_nonexistent_product(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
    ) -> None:
        """Альтернативный поток: создание заказа для несуществующего товара -> 404 ProductNotFound."""
        response = client.post(
            "/api/users/me/orders",
            headers=student_auth_headers,
            json={"product_id": str(uuid4()), "quantity": 1},
        )
        assert response.status_code == 404

    def test_create_order_invalid_quantity(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
        sample_product: Product,
    ) -> None:
        """Альтернативный поток: создание заказа с неположительным количеством (<=0) -> 422."""
        response = client.post(
            "/api/users/me/orders",
            headers=student_auth_headers,
            json={"product_id": str(sample_product.id), "quantity": 0},
        )
        assert response.status_code == 422

    def test_get_foreign_order_me(
        self,
        client: TestClient,
        teacher_auth_headers: dict[str, str],
        student_auth_headers: dict[str, str],
        sample_product: Product,
    ) -> None:
        """Альтернативный поток: студент пытается получить заказ преподавателя через /me/orders/{id} -> 404."""
        # Преподаватель создает заказ
        resp = client.post(
            "/api/users/me/orders",
            headers=teacher_auth_headers,
            json={"product_id": str(sample_product.id), "quantity": 1},
        )
        teacher_order_id = resp.json()["id"]

        # Студент пытается его прочитать
        student_resp = client.get(
            f"/api/users/me/orders/{teacher_order_id}",
            headers=student_auth_headers,
        )
        assert student_resp.status_code == 404

    def test_cancel_already_approved_order(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
        admin_auth_headers: dict[str, str],
        sample_product: Product,
    ) -> None:
        """Альтернативный поток: попытка отменить уже одобренный заказ -> 400 InvalidOrderStatus."""
        resp = client.post(
            "/api/users/me/orders",
            headers=student_auth_headers,
            json={"product_id": str(sample_product.id), "quantity": 1},
        )
        order_id = resp.json()["id"]

        # Админ подтверждает заказ
        client.post(
            f"/api/orders/{order_id}/approve",
            headers=admin_auth_headers,
        )

        # Студент пробует отменить
        cancel_resp = client.post(
            f"/api/users/me/orders/{order_id}/cancel",
            headers=student_auth_headers,
        )
        assert cancel_resp.status_code == 400
        assert (
            "Невозможно отменить заказ со статусом APPROVED"
            in cancel_resp.json().get("detail", "")
        )

    def test_approve_already_approved_order(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
        admin_auth_headers: dict[str, str],
        sample_product: Product,
    ) -> None:
        """Альтернативный поток: повторный approve заказа -> 400 InvalidOrderStatus."""
        resp = client.post(
            "/api/users/me/orders",
            headers=student_auth_headers,
            json={"product_id": str(sample_product.id), "quantity": 1},
        )
        order_id = resp.json()["id"]

        # Первый approve
        client.post(f"/api/orders/{order_id}/approve", headers=admin_auth_headers)

        # Второй approve
        second_resp = client.post(
            f"/api/orders/{order_id}/approve",
            headers=admin_auth_headers,
        )
        assert second_resp.status_code == 400

    def test_order_admin_endpoints_forbidden_for_student(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
    ) -> None:
        """Альтернативный поток: студент пытается вызвать админские эндпоинты заказов -> 403 Forbidden."""
        fake_id = uuid4()
        assert (
            client.get("/api/orders", headers=student_auth_headers).status_code == 403
        )
        assert (
            client.get(
                f"/api/orders/{fake_id}", headers=student_auth_headers
            ).status_code
            == 403
        )
        assert (
            client.post(
                f"/api/orders/{fake_id}/approve", headers=student_auth_headers
            ).status_code
            == 403
        )
        assert (
            client.post(
                f"/api/orders/{fake_id}/reject", headers=student_auth_headers
            ).status_code
            == 403
        )
