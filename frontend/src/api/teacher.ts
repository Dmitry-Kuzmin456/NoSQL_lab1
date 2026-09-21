import { api } from "./client";
import type { TeacherProfile } from "./types";

function prefix(teacherId?: string): string {
  return teacherId ? `/api/users/${teacherId}/teacher` : "/api/users/me/teacher";
}

export function getTeacher(teacherId?: string): Promise<TeacherProfile> {
  return api<TeacherProfile>(prefix(teacherId));
}

export function addStudent(studentId: string, teacherId?: string): Promise<TeacherProfile> {
  return api<TeacherProfile>(`${prefix(teacherId)}/students`, {
    method: "POST",
    body: JSON.stringify({ student_id: studentId }),
  });
}

export function removeStudent(studentId: string, teacherId?: string): Promise<TeacherProfile> {
  return api<TeacherProfile>(`${prefix(teacherId)}/students/${studentId}`, {
    method: "DELETE",
  });
}

export function recommendProduct(
  productId: string,
  teacherId?: string,
): Promise<{ product_id: string; affected_students: number; student_ids: string[] }> {
  return api(`${prefix(teacherId)}/students/favourites`, {
    method: "POST",
    body: JSON.stringify({ product_id: productId }),
  });
}
