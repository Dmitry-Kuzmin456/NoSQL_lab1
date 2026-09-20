from uuid import uuid4

from fastapi.testclient import TestClient

from domain.user import User, UserRole
from tests.conftest import RepositoriesContainer


class TestUsersFunctional:
    """Функциональные тесты управления пользователями (основной и альтернативный потоки)."""

    # -----------------------------------------------------------------------
    # Основной поток (Happy Path)
    # -----------------------------------------------------------------------

    def test_register_student_success(
        self,
        client: TestClient,
        repos: RepositoriesContainer,
    ) -> None:
        """Основной поток: успешная регистрация нового студента."""
        payload = {
            "name": "Алексей Смирнов",
            "email": "alexey@edu.ru",
            "password": "securePassword123",
            "role": UserRole.STUDENT.value,
        }
        response = client.post("/api/users/register", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Алексей Смирнов"
        assert data["email"] == "alexey@edu.ru"
        assert data["role"] == UserRole.STUDENT.value
        assert "password" not in data
        assert "password_hash" not in data

        # Проверяем сохранение в репозитории
        saved = repos.user_repo.get_by_email("alexey@edu.ru")
        assert saved is not None
        assert saved.name == "Алексей Смирнов"

    def test_register_teacher_success(
        self,
        client: TestClient,
    ) -> None:
        """Основной поток: успешная регистрация преподавателя."""
        payload = {
            "name": "Мария Ивановна",
            "email": "maria.teacher@edu.ru",
            "password": "teacherPassword123",
            "role": UserRole.TEACHER.value,
        }
        response = client.post("/api/users/register", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["role"] == UserRole.TEACHER.value

    def test_get_me_success(
        self,
        client: TestClient,
        student_user: User,
        student_auth_headers: dict[str, str],
    ) -> None:
        """Основной поток: получение профиля текущего пользователя."""
        response = client.get("/api/users/me", headers=student_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(student_user.id)
        assert data["email"] == student_user.email
        assert data["name"] == student_user.name

    def test_admin_get_user_by_id_success(
        self,
        client: TestClient,
        student_user: User,
        admin_auth_headers: dict[str, str],
    ) -> None:
        """Основной поток: администратор получает профиль пользователя по ID."""
        response = client.get(
            f"/api/users/{student_user.id}",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(student_user.id)
        assert data["email"] == student_user.email

    def test_update_profile_me_success(
        self,
        client: TestClient,
        student_user: User,
        student_auth_headers: dict[str, str],
        repos: RepositoriesContainer,
    ) -> None:
        """Основной поток: обновление собственного профиля."""
        update_payload = {
            "name": "Иван Обновленный",
            "email": "new.student.email@edu.ru",
        }
        response = client.patch(
            "/api/users/me",
            headers=student_auth_headers,
            json=update_payload,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Иван Обновленный"
        assert data["email"] == "new.student.email@edu.ru"

        # Проверяем в БД
        updated = repos.user_repo.get_by_id(student_user.id)
        assert updated is not None
        assert updated.name == "Иван Обновленный"
        assert updated.email == "new.student.email@edu.ru"

    def test_admin_update_profile_by_id_success(
        self,
        client: TestClient,
        student_user: User,
        admin_auth_headers: dict[str, str],
        repos: RepositoriesContainer,
    ) -> None:
        """Основной поток: администратор обновляет профиль пользователя по ID."""
        update_payload = {"name": "Студент Отредактирован Админом"}
        response = client.patch(
            f"/api/users/{student_user.id}",
            headers=admin_auth_headers,
            json=update_payload,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Студент Отредактирован Админом"

        updated = repos.user_repo.get_by_id(student_user.id)
        assert updated is not None
        assert updated.name == "Студент Отредактирован Админом"

    def test_change_password_me_success(
        self,
        client: TestClient,
        student_user: User,
        student_auth_headers: dict[str, str],
    ) -> None:
        """Основной поток: смена пароля текущего пользователя."""
        change_payload = {
            "old_password": "password123",
            "new_password": "brandNewSecurePassword456",
        }
        response = client.post(
            "/api/users/me/change-password",
            headers=student_auth_headers,
            json=change_payload,
        )
        assert response.status_code == 204

        # Вход со старым паролем должен завершиться ошибкой 401
        old_login = client.post(
            "/api/auth/login",
            json={"email": student_user.email, "password": "password123"},
        )
        assert old_login.status_code == 401

        # Вход с новым паролем успешен
        new_login = client.post(
            "/api/auth/login",
            json={
                "email": student_user.email,
                "password": "brandNewSecurePassword456",
            },
        )
        assert new_login.status_code == 200

    def test_admin_change_password_by_id_success(
        self,
        client: TestClient,
        student_user: User,
        admin_auth_headers: dict[str, str],
    ) -> None:
        """Основной поток: администратор меняет пароль пользователя по ID."""
        change_payload = {
            "old_password": "password123",
            "new_password": "adminAssignedPassword789",
        }
        response = client.post(
            f"/api/users/{student_user.id}/change-password",
            headers=admin_auth_headers,
            json=change_payload,
        )
        assert response.status_code == 204

        # Вход с новым паролем
        new_login = client.post(
            "/api/auth/login",
            json={
                "email": student_user.email,
                "password": "adminAssignedPassword789",
            },
        )
        assert new_login.status_code == 200

    def test_delete_user_me_success(
        self,
        client: TestClient,
        student_user: User,
        student_auth_headers: dict[str, str],
        repos: RepositoriesContainer,
    ) -> None:
        """Основной поток: удаление собственного профиля."""
        response = client.delete("/api/users/me", headers=student_auth_headers)
        assert response.status_code == 204
        assert repos.user_repo.get_by_id(student_user.id) is None

    def test_admin_delete_user_by_id_success(
        self,
        client: TestClient,
        student_user: User,
        admin_auth_headers: dict[str, str],
        repos: RepositoriesContainer,
    ) -> None:
        """Основной поток: администратор удаляет пользователя по ID."""
        response = client.delete(
            f"/api/users/{student_user.id}",
            headers=admin_auth_headers,
        )
        assert response.status_code == 204
        assert repos.user_repo.get_by_id(student_user.id) is None

    # -----------------------------------------------------------------------
    # Альтернативные потоки (Alternative Flows & Errors)
    # -----------------------------------------------------------------------

    def test_register_duplicate_email(
        self,
        client: TestClient,
        student_user: User,
    ) -> None:
        """Альтернативный поток: регистрация с уже существующим email -> 409 Conflict."""
        payload = {
            "name": "Другой Иван",
            "email": student_user.email.upper(),  # Регистронезависимая проверка
            "password": "password123",
            "role": UserRole.STUDENT.value,
        }
        response = client.post("/api/users/register", json=payload)
        assert response.status_code == 409
        assert "detail" in response.json()

    def test_register_weak_password(
        self,
        client: TestClient,
    ) -> None:
        """Альтернативный поток: регистрация со слишком коротким паролем (<6) -> 422/400."""
        payload = {
            "name": "Слабый Пароль",
            "email": "weak@edu.ru",
            "password": "123",
            "role": UserRole.STUDENT.value,
        }
        response = client.post("/api/users/register", json=payload)
        assert response.status_code in (400, 422)

    def test_register_invalid_email(
        self,
        client: TestClient,
    ) -> None:
        """Альтернативный поток: некорректный email при регистрации -> 422."""
        payload = {
            "name": "Некорректный Email",
            "email": "invalid-email-address",
            "password": "securePassword123",
            "role": UserRole.STUDENT.value,
        }
        response = client.post("/api/users/register", json=payload)
        assert response.status_code == 422

    def test_get_me_unauthenticated(
        self,
        client: TestClient,
    ) -> None:
        """Альтернативный поток: запрос /me без авторизации -> 401."""
        response = client.get("/api/users/me")
        assert response.status_code == 401

    def test_get_user_by_id_forbidden_for_student(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
        teacher_user: User,
    ) -> None:
        """Альтернативный поток: студент пытается получить пользователя по ID -> 403."""
        response = client.get(
            f"/api/users/{teacher_user.id}",
            headers=student_auth_headers,
        )
        assert response.status_code == 403

    def test_get_user_by_id_forbidden_for_teacher(
        self,
        client: TestClient,
        teacher_auth_headers: dict[str, str],
        student_user: User,
    ) -> None:
        """Альтернативный поток: преподаватель пытается получить пользователя по ID -> 403."""
        response = client.get(
            f"/api/users/{student_user.id}",
            headers=teacher_auth_headers,
        )
        assert response.status_code == 403

    def test_admin_get_nonexistent_user_by_id(
        self,
        client: TestClient,
        admin_auth_headers: dict[str, str],
    ) -> None:
        """Альтернативный поток: администратор запрашивает несуществующий ID -> 404."""
        response = client.get(
            f"/api/users/{uuid4()}",
            headers=admin_auth_headers,
        )
        assert response.status_code == 404

    def test_update_profile_me_unauthenticated(
        self,
        client: TestClient,
    ) -> None:
        """Альтернативный поток: обновление профиля без авторизации -> 401."""
        response = client.patch(
            "/api/users/me",
            json={"name": "Аноним"},
        )
        assert response.status_code == 401

    def test_update_profile_duplicate_email(
        self,
        client: TestClient,
        student_user: User,
        teacher_user: User,
        student_auth_headers: dict[str, str],
    ) -> None:
        """Альтернативный поток: смена email на занятый другим пользователем -> 409."""
        response = client.patch(
            "/api/users/me",
            headers=student_auth_headers,
            json={"email": teacher_user.email},
        )
        assert response.status_code == 409

    def test_update_user_by_id_forbidden_for_student(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
        teacher_user: User,
    ) -> None:
        """Альтернативный поток: студент пытается изменить другого пользователя -> 403."""
        response = client.patch(
            f"/api/users/{teacher_user.id}",
            headers=student_auth_headers,
            json={"name": "Взломщик"},
        )
        assert response.status_code == 403

    def test_admin_update_nonexistent_user(
        self,
        client: TestClient,
        admin_auth_headers: dict[str, str],
    ) -> None:
        """Альтернативный поток: обновление несуществующего пользователя -> 404."""
        response = client.patch(
            f"/api/users/{uuid4()}",
            headers=admin_auth_headers,
            json={"name": "Призрак"},
        )
        assert response.status_code == 404

    def test_change_password_me_wrong_old_password(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
    ) -> None:
        """Альтернативный поток: неверный старый пароль -> 401 InvalidCredentials."""
        response = client.post(
            "/api/users/me/change-password",
            headers=student_auth_headers,
            json={
                "old_password": "incorrectOldPassword",
                "new_password": "validNewPassword123",
            },
        )
        assert response.status_code == 401

    def test_change_password_me_weak_new_password(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
    ) -> None:
        """Альтернативный поток: новый пароль короче 6 символов -> 422/400."""
        response = client.post(
            "/api/users/me/change-password",
            headers=student_auth_headers,
            json={"old_password": "password123", "new_password": "123"},
        )
        assert response.status_code in (400, 422)

    def test_change_password_by_id_forbidden_for_student(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
        teacher_user: User,
    ) -> None:
        """Альтернативный поток: студент пытается сменить пароль другого пользователя -> 403."""
        response = client.post(
            f"/api/users/{teacher_user.id}/change-password",
            headers=student_auth_headers,
            json={
                "old_password": "password123",
                "new_password": "newPassword123",
            },
        )
        assert response.status_code == 403

    def test_delete_user_me_unauthenticated(
        self,
        client: TestClient,
    ) -> None:
        """Альтернативный поток: удаление профиля без авторизации -> 401."""
        response = client.delete("/api/users/me")
        assert response.status_code == 401

    def test_delete_user_by_id_forbidden_for_student(
        self,
        client: TestClient,
        student_auth_headers: dict[str, str],
        teacher_user: User,
    ) -> None:
        """Альтернативный поток: студент пытается удалить другого пользователя -> 403."""
        response = client.delete(
            f"/api/users/{teacher_user.id}",
            headers=student_auth_headers,
        )
        assert response.status_code == 403

    def test_admin_delete_nonexistent_user(
        self,
        client: TestClient,
        admin_auth_headers: dict[str, str],
    ) -> None:
        """Альтернативный поток: удаление несуществующего пользователя -> 404."""
        response = client.delete(
            f"/api/users/{uuid4()}",
            headers=admin_auth_headers,
        )
        assert response.status_code == 404

    def test_repository_get_by_ids(
        self,
        repos: RepositoriesContainer,
        student_user: User,
        teacher_user: User,
    ) -> None:
        """Проверка пакетного получения пользователей через get_by_ids."""
        # Пустой список
        assert repos.user_repo.get_by_ids([]) == []

        # Несколько существующих пользователей
        found = repos.user_repo.get_by_ids([student_user.id, teacher_user.id])
        assert len(found) == 2
        found_ids = {u.id for u in found}
        assert student_user.id in found_ids
        assert teacher_user.id in found_ids

        # Смесь существующих и несуществующего ID
        non_existent_id = uuid4()
        found_mixed = repos.user_repo.get_by_ids([student_user.id, non_existent_id])
        assert len(found_mixed) == 1
        assert found_mixed[0].id == student_user.id
