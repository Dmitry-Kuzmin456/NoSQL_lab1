from uuid import uuid4

from fastapi.testclient import TestClient

from domain.product import Product
from domain.teacher import Teacher
from domain.user import User, UserRole
from tests.conftest import RepositoriesContainer


class TestTeacherFunctional:
    """Функциональные тесты сценариев преподавателя и работы со студентами (основной и альтернативный потоки)."""

    # -----------------------------------------------------------------------
    # Основной поток (Happy Path)
    # -----------------------------------------------------------------------

    def test_get_my_teacher_profile(
        self,
        client: TestClient,
        teacher_user: Teacher,
        teacher_auth_headers: dict[str, str],
    ) -> None:
        """Основной поток: преподаватель получает свой профиль со списком ID студентов."""
        response = client.get("/api/users/me/teacher", headers=teacher_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(teacher_user.id)
        assert data["email"] == teacher_user.email
        assert data["role"] == UserRole.TEACHER.value
        assert isinstance(data["student_ids"], list)
        assert data["total_students"] == 0

    def test_add_student_and_get_students_list(
        self,
        client: TestClient,
        teacher_user: Teacher,
        teacher_auth_headers: dict[str, str],
        student_user: User,
    ) -> None:
        """Основной поток: преподаватель прикрепляет студента и получает подробный список своих студентов."""
        # 1. Прикрепляем студента
        add_resp = client.post(
            "/api/users/me/teacher/students",
            headers=teacher_auth_headers,
            json={"student_id": str(student_user.id)},
        )
        assert add_resp.status_code == 200
        teacher_data = add_resp.json()
        assert str(student_user.id) in teacher_data["student_ids"]
        assert teacher_data["total_students"] == 1
        assert len(teacher_data["students"]) == 1
        assert teacher_data["students"][0]["id"] == str(student_user.id)
        assert teacher_data["students"][0]["name"] == student_user.name
        assert teacher_data["students"][0]["email"] == student_user.email

        # 2. Получаем подробный список студентов
        students_resp = client.get(
            "/api/users/me/teacher/students",
            headers=teacher_auth_headers,
        )
        assert students_resp.status_code == 200
        students = students_resp.json()
        assert len(students) == 1
        assert students[0]["id"] == str(student_user.id)

        assert students[0]["name"] == student_user.name
        assert students[0]["email"] == student_user.email

    def test_teacher_batch_add_product_to_all_students_favourites(
        self,
        client: TestClient,
        teacher_user: Teacher,
        teacher_auth_headers: dict[str, str],
        student_user: User,
        sample_product: Product,
        repos: RepositoriesContainer,
    ) -> None:
        """Основной поток (ключевой сценарий ЛР): преподаватель рекомендует товар всем своим ученикам."""
        # Прикрепляем студента
        client.post(
            "/api/users/me/teacher/students",
            headers=teacher_auth_headers,
            json={"student_id": str(student_user.id)},
        )

        # Пакетно рекомендуем товар
        response = client.post(
            "/api/users/me/teacher/students/favourites",
            headers=teacher_auth_headers,
            json={"product_id": str(sample_product.id)},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["product_id"] == str(sample_product.id)
        assert data["affected_students"] == 1
        assert str(student_user.id) in data["student_ids"]

        # Проверяем, что товар появился в избранном у студента с пометкой added_user_id = teacher_user.id
        student_favs = repos.favourites_repo.get_by_user_id(student_user.id)
        assert student_favs is not None
        assert student_favs.has_product(sample_product.id)
        item = next(
            p for p in student_favs.products if p.product_id == sample_product.id
        )
        assert item.added_user_id == teacher_user.id

    def test_remove_student_success(
        self,
        client: TestClient,
        teacher_user: Teacher,
        teacher_auth_headers: dict[str, str],
        student_user: User,
    ) -> None:
        """Основной поток: преподаватель открепляет студента."""
        # Прикрепляем
        client.post(
            "/api/users/me/teacher/students",
            headers=teacher_auth_headers,
            json={"student_id": str(student_user.id)},
        )
        # Открепляем
        del_resp = client.delete(
            f"/api/users/me/teacher/students/{student_user.id}",
            headers=teacher_auth_headers,
        )
        assert del_resp.status_code == 200
        assert str(student_user.id) not in del_resp.json()["student_ids"]
        assert del_resp.json()["total_students"] == 0

    def test_admin_manage_teacher_students_success(
        self,
        client: TestClient,
        teacher_user: Teacher,
        student_user: User,
        admin_auth_headers: dict[str, str],
        sample_product: Product,
    ) -> None:
        """Основной поток: администратор управляет списком студентов преподавателя по его ID."""
        # Админ получает профиль преподавателя
        prof_resp = client.get(
            f"/api/users/{teacher_user.id}/teacher",
            headers=admin_auth_headers,
        )
        assert prof_resp.status_code == 200

        # Админ прикрепляет студента
        add_resp = client.post(
            f"/api/users/{teacher_user.id}/teacher/students",
            headers=admin_auth_headers,
            json={"student_id": str(student_user.id)},
        )
        assert add_resp.status_code == 200
        assert add_resp.json()["total_students"] == 1

        # Админ выполняет пакетное добавление товара студентам
        batch_resp = client.post(
            f"/api/users/{teacher_user.id}/teacher/students/favourites",
            headers=admin_auth_headers,
            json={"product_id": str(sample_product.id)},
        )
        assert batch_resp.status_code == 200
        assert batch_resp.json()["affected_students"] == 1

        # Админ открепляет студента
        del_resp = client.delete(
            f"/api/users/{teacher_user.id}/teacher/students/{student_user.id}",
            headers=admin_auth_headers,
        )
        assert del_resp.status_code == 200
        assert del_resp.json()["total_students"] == 0

    # -----------------------------------------------------------------------
    # Альтернативные потоки (Alternative Flows & Errors)
    # -----------------------------------------------------------------------

    def test_get_teacher_profile_forbidden_for_student(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
    ) -> None:
        """Альтернативный поток: студент пытается открыть профиль преподавателя -> 403 Forbidden."""
        response = client.get("/api/users/me/teacher", headers=student_auth_headers)
        assert response.status_code == 403

    def test_teacher_add_self_as_student(
        self,
        client: TestClient,
        teacher_user: Teacher,
        teacher_auth_headers: dict[str, str],
    ) -> None:
        """Альтернативный поток: преподаватель пытается добавить себя в ученики -> 400 CannotAddSelfAsStudent."""
        response = client.post(
            "/api/users/me/teacher/students",
            headers=teacher_auth_headers,
            json={"student_id": str(teacher_user.id)},
        )
        assert response.status_code == 400
        assert "сам себя" in response.json().get("detail", "")

    def test_teacher_add_nonexistent_student(
        self,
        client: TestClient,
        teacher_auth_headers: dict[str, str],
    ) -> None:
        """Альтернативный поток: прикрепление несуществующего студента -> 404 UserNotFound."""
        response = client.post(
            "/api/users/me/teacher/students",
            headers=teacher_auth_headers,
            json={"student_id": str(uuid4())},
        )
        assert response.status_code == 404

    def test_teacher_add_non_student_role(
        self,
        client: TestClient,
        teacher_auth_headers: dict[str, str],
        admin_user: User,
    ) -> None:
        """Альтернативный поток: попытка прикрепить пользователя с ролью ADMIN -> 400 InvalidStudentRole."""
        response = client.post(
            "/api/users/me/teacher/students",
            headers=teacher_auth_headers,
            json={"student_id": str(admin_user.id)},
        )
        assert response.status_code == 400
        assert "не является учеником" in response.json().get("detail", "")

    def test_teacher_add_already_assigned_student(
        self,
        client: TestClient,
        teacher_auth_headers: dict[str, str],
        student_user: User,
    ) -> None:
        """Альтернативный поток: повторное прикрепление уже прикрепленного ученика -> 409 StudentAlreadyAssigned."""
        # Первый раз
        client.post(
            "/api/users/me/teacher/students",
            headers=teacher_auth_headers,
            json={"student_id": str(student_user.id)},
        )
        # Второй раз
        second_resp = client.post(
            "/api/users/me/teacher/students",
            headers=teacher_auth_headers,
            json={"student_id": str(student_user.id)},
        )
        assert second_resp.status_code == 409
        assert "уже прикреплен" in second_resp.json().get("detail", "")

    def test_teacher_remove_unassigned_student(
        self,
        client: TestClient,
        teacher_auth_headers: dict[str, str],
        student_user: User,
    ) -> None:
        """Альтернативный поток: открепление ученика, который не был прикреплен -> 404 StudentNotAssigned."""
        response = client.delete(
            f"/api/users/me/teacher/students/{student_user.id}",
            headers=teacher_auth_headers,
        )
        assert response.status_code == 404
        assert "не найден в списке учеников" in response.json().get("detail", "")

    def test_teacher_batch_add_nonexistent_product(
        self,
        client: TestClient,
        teacher_auth_headers: dict[str, str],
        student_user: User,
    ) -> None:
        """Альтернативный поток: рекомендация несуществующего товара -> 404 ProductNotFound."""
        client.post(
            "/api/users/me/teacher/students",
            headers=teacher_auth_headers,
            json={"student_id": str(student_user.id)},
        )

        response = client.post(
            "/api/users/me/teacher/students/favourites",
            headers=teacher_auth_headers,
            json={"product_id": str(uuid4())},
        )
        assert response.status_code == 404

    def test_teacher_batch_add_product_zero_students(
        self,
        client: TestClient,
        teacher_auth_headers: dict[str, str],
        sample_product: Product,
    ) -> None:
        """Альтернативный поток: рекомендация товара при отсутствии прикрепленных студентов -> 200, affected=0."""
        response = client.post(
            "/api/users/me/teacher/students/favourites",
            headers=teacher_auth_headers,
            json={"product_id": str(sample_product.id)},
        )
        assert response.status_code == 200
        assert response.json()["affected_students"] == 0
        assert response.json()["student_ids"] == []

    def test_admin_teacher_endpoints_forbidden_for_student(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
        teacher_user: Teacher,
    ) -> None:
        """Альтернативный поток: студент пытается вызвать админские эндпоинты преподавателя -> 403."""
        fake_id = teacher_user.id
        assert (
            client.get(
                f"/api/users/{fake_id}/teacher", headers=student_auth_headers
            ).status_code
            == 403
        )
        assert (
            client.get(
                f"/api/users/{fake_id}/teacher/students", headers=student_auth_headers
            ).status_code
            == 403
        )
        assert (
            client.post(
                f"/api/users/{fake_id}/teacher/students",
                headers=student_auth_headers,
                json={"student_id": str(uuid4())},
            ).status_code
            == 403
        )
