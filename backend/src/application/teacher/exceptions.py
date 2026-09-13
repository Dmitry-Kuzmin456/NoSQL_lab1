from uuid import UUID

from application.exceptions import ApplicationException


class TeacherException(ApplicationException):
    """Базовое исключение для операций с преподавателями."""

    status_code: int = 400


class TeacherNotFoundException(TeacherException):
    status_code: int = 404

    def __init__(self, teacher_id: UUID):
        super().__init__(f"Преподаватель '{teacher_id}' не найден.")
        self.teacher_id = teacher_id


class CannotAddSelfAsStudentException(TeacherException):
    status_code: int = 400

    def __init__(self):
        super().__init__("Преподаватель не может добавить сам себя в список своих учеников.")


class StudentAlreadyAssignedException(TeacherException):
    status_code: int = 409

    def __init__(self, student_id: UUID):
        super().__init__(f"Ученик '{student_id}' уже прикреплен к этому преподавателю.")
        self.student_id = student_id


class StudentNotAssignedException(TeacherException):
    status_code: int = 404

    def __init__(self, student_id: UUID):
        super().__init__(f"Ученик '{student_id}' не найден в списке учеников преподавателя.")
        self.student_id = student_id


class InvalidStudentRoleException(TeacherException):
    status_code: int = 400

    def __init__(self, user_id: UUID):
        super().__init__(f"Пользователь '{user_id}' не является учеником (роль должна быть STUDENT).")
        self.user_id = user_id
