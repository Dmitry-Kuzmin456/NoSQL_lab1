from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from domain.product import Product
from domain.user import User


class TestCartFunctional:
    """Функциональные тесты корзины покупок (основной и альтернативный потоки)."""

    # -----------------------------------------------------------------------
    # Основной поток (Happy Path)
    # -----------------------------------------------------------------------

    def test_get_empty_cart_me(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
        student_user: User,
    ) -> None:
        """Основной поток: получение пустой корзины текущего пользователя."""
        response = client.get("/api/users/me/cart", headers=student_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == str(student_user.id)
        assert data["items"] == []
        assert data["total_items"] == 0

    def test_add_and_update_cart_items_me(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
        sample_product: Product,
    ) -> None:
        """Основной поток: добавление и изменение количества товара в корзине."""
        # 1. Добавляем 2 шт
        resp1 = client.patch(
            f"/api/users/me/cart/items/{sample_product.id}",
            headers=student_auth_headers,
            json={"quantity": 2},
        )
        assert resp1.status_code == 200
        data1 = resp1.json()
        assert data1["total_items"] == 2
        assert Decimal(str(data1["total_amount"])) == Decimal("3000.00")
        assert not data1["has_unavailable_items"]
        assert len(data1["items"]) == 1
        item1 = data1["items"][0]
        assert item1["product_id"] == str(sample_product.id)
        assert item1["quantity"] == 2
        assert item1["product"]["name"] == sample_product.name
        assert Decimal(str(item1["product"]["price"])) == Decimal("1500.00")
        assert Decimal(str(item1["subtotal"])) == Decimal("3000.00")
        assert item1["is_available"] is True
        assert item1["available_stock"] == 10

        # 2. Обновляем до 5 шт
        resp2 = client.patch(
            f"/api/users/me/cart/items/{sample_product.id}",
            headers=student_auth_headers,
            json={"quantity": 5},
        )
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["total_items"] == 5
        assert Decimal(str(data2["total_amount"])) == Decimal("7500.00")
        assert data2["items"][0]["quantity"] == 5
        assert Decimal(str(data2["items"][0]["subtotal"])) == Decimal("7500.00")

    def test_update_cart_quantity_zero_removes_item(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
        sample_product: Product,
    ) -> None:
        """Основной поток: установка количества = 0 удаляет товар из корзины."""
        # Добавляем
        client.patch(
            f"/api/users/me/cart/items/{sample_product.id}",
            headers=student_auth_headers,
            json={"quantity": 3},
        )
        # Ставим 0
        resp = client.patch(
            f"/api/users/me/cart/items/{sample_product.id}",
            headers=student_auth_headers,
            json={"quantity": 0},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_items"] == 0
        assert len(data["items"]) == 0

    def test_remove_cart_item_me_success(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
        sample_product: Product,
    ) -> None:
        """Основной поток: явное удаление товара из корзины через DELETE."""
        client.patch(
            f"/api/users/me/cart/items/{sample_product.id}",
            headers=student_auth_headers,
            json={"quantity": 4},
        )

        resp = client.delete(
            f"/api/users/me/cart/items/{sample_product.id}",
            headers=student_auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["total_items"] == 0

    def test_clear_cart_me_success(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
        sample_product: Product,
    ) -> None:
        """Основной поток: полная очистка корзины."""
        client.patch(
            f"/api/users/me/cart/items/{sample_product.id}",
            headers=student_auth_headers,
            json={"quantity": 2},
        )

        resp = client.delete(
            "/api/users/me/cart",
            headers=student_auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["items"] == []
        assert resp.json()["total_items"] == 0

    def test_admin_manage_user_cart_success(
        self,
        client: TestClient,
        student_user: User,
        admin_auth_headers: dict[str, str],
        sample_product: Product,
    ) -> None:
        """Основной поток: администратор просматривает, изменяет и очищает корзину пользователя."""
        # Админ добавляет товар в корзину студента
        resp_add = client.patch(
            f"/api/users/{student_user.id}/cart/items/{sample_product.id}",
            headers=admin_auth_headers,
            json={"quantity": 3},
        )
        assert resp_add.status_code == 200
        assert resp_add.json()["total_items"] == 3

        # Админ получает корзину студента
        resp_get = client.get(
            f"/api/users/{student_user.id}/cart",
            headers=admin_auth_headers,
        )
        assert resp_get.status_code == 200
        assert resp_get.json()["total_items"] == 3

        # Админ удаляет товар
        resp_del = client.delete(
            f"/api/users/{student_user.id}/cart/items/{sample_product.id}",
            headers=admin_auth_headers,
        )
        assert resp_del.status_code == 200
        assert resp_del.json()["total_items"] == 0

        # Админ очищает корзину
        resp_clear = client.delete(
            f"/api/users/{student_user.id}/cart",
            headers=admin_auth_headers,
        )
        assert resp_clear.status_code == 200

    # -----------------------------------------------------------------------
    # Альтернативные потоки (Alternative Flows & Errors)
    # -----------------------------------------------------------------------

    def test_get_cart_me_unauthenticated(
        self,
        client: TestClient,
    ) -> None:
        """Альтернативный поток: получение корзины без авторизации -> 401."""
        response = client.get("/api/users/me/cart")
        assert response.status_code == 401

    def test_get_cart_by_user_id_forbidden_for_student(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
        teacher_user: User,
    ) -> None:
        """Альтернативный поток: студент пытается посмотреть корзину другого пользователя -> 403."""
        response = client.get(
            f"/api/users/{teacher_user.id}/cart",
            headers=student_auth_headers,
        )
        assert response.status_code == 403

    def test_add_nonexistent_product_to_cart(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
    ) -> None:
        """Альтернативный поток: добавление несуществующего товара -> 404 ProductNotFound."""
        response = client.patch(
            f"/api/users/me/cart/items/{uuid4()}",
            headers=student_auth_headers,
            json={"quantity": 1},
        )
        assert response.status_code == 404

    def test_update_cart_negative_quantity(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
        sample_product: Product,
    ) -> None:
        """Альтернативный поток: передача отрицательного количества -> 422."""
        response = client.patch(
            f"/api/users/me/cart/items/{sample_product.id}",
            headers=student_auth_headers,
            json={"quantity": -1},
        )
        assert response.status_code == 422

    def test_remove_product_not_in_cart(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
        sample_product: Product,
    ) -> None:
        """Альтернативный поток: удаление товара, которого нет в корзине -> 404 CartProductNotFound."""
        response = client.delete(
            f"/api/users/me/cart/items/{sample_product.id}",
            headers=student_auth_headers,
        )
        assert response.status_code == 404
        assert "не найден в корзине" in response.json().get("detail", "")

    def test_update_cart_by_user_id_forbidden_for_student(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
        teacher_user: User,
        sample_product: Product,
    ) -> None:
        """Альтернативный поток: студент пытается изменить чужую корзину -> 403."""
        response = client.patch(
            f"/api/users/{teacher_user.id}/cart/items/{sample_product.id}",
            headers=student_auth_headers,
            json={"quantity": 1},
        )
        assert response.status_code == 403

    def test_clear_cart_by_user_id_forbidden_for_student(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
        teacher_user: User,
    ) -> None:
        """Альтернативный поток: студент пытается очистить чужую корзину -> 403."""
        response = client.delete(
            f"/api/users/{teacher_user.id}/cart",
            headers=student_auth_headers,
        )
        assert response.status_code == 403
