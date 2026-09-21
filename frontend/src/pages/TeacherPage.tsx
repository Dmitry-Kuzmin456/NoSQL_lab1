import { FormEvent, useEffect, useState } from "react";
import { getUserByEmail } from "../api/auth";
import { ApiError } from "../api/client";
import { listProducts } from "../api/products";
import { addStudent, getTeacher, recommendProduct, removeStudent } from "../api/teacher";
import type { Product, TeacherProfile } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { roleLabel } from "../lib/format";

function pickProductByName(name: string, items: Product[]): Product | string {
  const needle = name.trim().toLowerCase();
  const exact = items.filter((item) => item.name.trim().toLowerCase() === needle);
  if (exact.length === 1) return exact[0];
  if (exact.length > 1) return "Несколько товаров с таким названием — уточните";
  if (items.length === 1) return items[0];
  if (items.length === 0) return "Товар с таким названием не найден";
  return "Уточните название, нашлось несколько товаров";
}

export function TeacherPage() {
  const { user } = useAuth();
  const isAdmin = user?.role === "ADMIN";
  const [teacherEmail, setTeacherEmail] = useState("");
  const [activeTeacherId, setActiveTeacherId] = useState<string | undefined>(undefined);
  const [profile, setProfile] = useState<TeacherProfile | null>(null);
  const [studentEmail, setStudentEmail] = useState("");
  const [productName, setProductName] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(!isAdmin);

  async function load(id?: string) {
    setLoading(true);
    setError("");
    try {
      const next = await getTeacher(id);
      setProfile(next);
    } catch (err) {
      setProfile(null);
      setError(err instanceof ApiError ? err.message : "Не удалось загрузить учеников");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!isAdmin) void load();
  }, [isAdmin]);

  async function onLoadTeacher(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      const teacher = await getUserByEmail(teacherEmail.trim());
      if (teacher.role !== "TEACHER" && teacher.role !== "ADMIN") {
        setProfile(null);
        setError("Это не преподаватель");
        return;
      }
      setActiveTeacherId(teacher.id);
      await load(teacher.id);
    } catch (err) {
      setProfile(null);
      setError(err instanceof ApiError ? err.message : "Не удалось найти преподавателя");
    }
  }

  async function onAdd(event: FormEvent) {
    event.preventDefault();
    setError("");
    setMessage("");
    try {
      const student = await getUserByEmail(studentEmail.trim());
      const next = await addStudent(student.id, activeTeacherId);
      setProfile(next);
      setStudentEmail("");
      setMessage("Ученик прикреплён");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось прикрепить");
    }
  }

  async function onRemove(id: string) {
    try {
      const next = await removeStudent(id, activeTeacherId);
      setProfile(next);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось открепить");
    }
  }

  async function onRecommend(event: FormEvent) {
    event.preventDefault();
    setError("");
    setMessage("");
    try {
      const name = productName.trim();
      const catalog = await listProducts({ query: name, limit: 50, sort_by: "name_asc" });
      const picked = pickProductByName(name, catalog.items);
      if (typeof picked === "string") {
        setError(picked);
        return;
      }
      const result = await recommendProduct(picked.id, activeTeacherId);
      setMessage(
        `«${picked.name}» добавлен в избранное ${result.affected_students} прикреплённым ученикам`,
      );
      setProductName("");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось рекомендовать товар");
    }
  }

  return (
    <>
      <h1>Ученики</h1>
      {isAdmin ? (
        <form className="card filters" onSubmit={onLoadTeacher} style={{ gridTemplateColumns: "1fr auto" }}>
          <label className="field">
            <span>Email преподавателя</span>
            <input
              type="email"
              required
              value={teacherEmail}
              onChange={(event) => setTeacherEmail(event.target.value)}
            />
          </label>
          <button className="btn btn--primary" type="submit">
            Открыть
          </button>
        </form>
      ) : null}
      {error ? <p className="error">{error}</p> : null}
      {message ? <p className="ok">{message}</p> : null}
      {loading ? <div className="skeleton" /> : null}
      {profile ? (
        <>
          <p className="muted" style={{ marginBottom: 16 }}>
            {profile.name} · {profile.email} · учеников: {profile.total_students}
          </p>
          <form className="card filters" onSubmit={onAdd} style={{ gridTemplateColumns: "1fr auto" }}>
            <label className="field">
              <span>Email ученика</span>
              <input
                type="email"
                required
                value={studentEmail}
                onChange={(event) => setStudentEmail(event.target.value)}
              />
            </label>
            <button className="btn btn--primary" type="submit">
              Прикрепить
            </button>
          </form>
          <form className="card filters" onSubmit={onRecommend} style={{ gridTemplateColumns: "1fr auto" }}>
            <label className="field">
              <span>Название товара — в избранное всем прикреплённым</span>
              <input
                required
                value={productName}
                onChange={(event) => setProductName(event.target.value)}
                placeholder="Как в каталоге"
              />
            </label>
            <button className="btn btn--ghost" type="submit">
              Рекомендовать
            </button>
          </form>
          {profile.students.length === 0 ? (
            <div className="card empty">Список пуст</div>
          ) : (
            <div className="list">
              {profile.students.map((student) => (
                <article key={student.id} className="card row">
                  <div className="row__main">
                    <strong>{student.name}</strong>
                    <span className="muted">
                      {student.email} · {roleLabel(student.role)}
                    </span>
                  </div>
                  <button type="button" className="btn btn--danger" onClick={() => void onRemove(student.id)}>
                    Открепить
                  </button>
                </article>
              ))}
            </div>
          )}
        </>
      ) : null}
    </>
  );
}
