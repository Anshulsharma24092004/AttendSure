# AttendSure Database Schema (MySQL)

This document describes the current database schema used by AttendSure.
It is based on the SQLAlchemy models in `backend/app/models`.

---

## 1) users

Stores both teachers and students.

**Primary Key**
- `id` (INT, PK)

**Columns**
- `id` (INT, PK, auto-increment)
- `name` (VARCHAR, not null)
- `email` (VARCHAR, not null, unique)
- `password_hash` (VARCHAR, not null) — stored using Werkzeug hashing
- `role` (VARCHAR, not null) — `teacher` or `student`
- `created_at` (DATETIME, default NOW)
- `is_active` (BOOLEAN, default TRUE)

---

## 2) classes

A class is created by a teacher and has a geo-fence location.

**Primary Key**
- `id`

**Foreign Keys**
- `teacher_id` → `users.id`

**Columns**
- `id` (INT, PK, auto-increment)
- `name` (VARCHAR(150), not null)
- `teacher_id` (INT, not null, FK → users.id)
- `latitude` (FLOAT, not null)
- `longitude` (FLOAT, not null)
- `radius_meters` (INT, not null)
- `is_active` (BOOLEAN, default TRUE)
- `created_at` (DATETIME, default NOW)

---

## 3) enrollments

Links students to classes (many-to-many relationship between users and classes).

**Primary Key**
- `id` (recommended)

**Foreign Keys**
- `student_id` → `users.id`
- `class_id` → `classes.id`

**Columns**
- `id` (INT, PK, auto-increment)
- `student_id` (INT, not null, FK → users.id)
- `class_id` (INT, not null, FK → classes.id)
- `created_at` (DATETIME, default NOW)
- `is_active` (BOOLEAN, default TRUE)

**Suggested Constraint**
- Unique(student_id, class_id) — prevents duplicate enrollment

---

## 4) attendance_sessions

A teacher starts an attendance session for a class.

**Primary Key**
- `id`

**Foreign Keys**
- `class_id` → `classes.id`
- `created_by` → `users.id` (teacher who started the session)

**Columns**
- `id` (INT, PK, auto-increment)
- `class_id` (INT, not null, FK → classes.id)
- `created_by` (INT, not null, FK → users.id)
- `starts_at` (DATETIME, not null)
- `ends_at` (DATETIME, not null)
- `attendance_code` (VARCHAR(20), not null)
- `is_active` (BOOLEAN, default TRUE)
- `created_at` (DATETIME, default NOW)

---

## 5) attendance_records

A student’s attendance submission for a session.

**Primary Key**
- `id`

**Foreign Keys**
- `student_id` → `users.id`
- `session_id` → `attendance_sessions.id`

**Columns**
- `id` (INT, PK, auto-increment)
- `student_id` (INT, not null, FK → users.id)
- `session_id` (INT, not null, FK → attendance_sessions.id)
- `status` (VARCHAR(20), not null, default 'present')
- `device_signature` (VARCHAR(255), nullable) — SHA-256 of device info bundle (evidence, not biometric)
- `ip_prefix` (VARCHAR(50), nullable) — stored as evidence when available
- `marked_at` (DATETIME, default NOW)

**Suggested Constraint**
- Unique(student_id, session_id) — prevents double attendance

---

## Relationship summary

- `users (teacher)` 1 → * `classes`
- `users (student)` * → * `classes` via `enrollments`
- `classes` 1 → * `attendance_sessions`
- `attendance_sessions` 1 → * `attendance_records`
- `users (student)` 1 → * `attendance_records`

---

## Notes on Verification Design

AttendSure verifies presence using:
- Session time window (`starts_at`, `ends_at`)
- Geo-fence check based on `classes.latitude/longitude/radius_meters`
- Attendance code (`attendance_code`)
- Evidence fields (`device_signature`, `ip_prefix`) for anomaly/dispute support

No biometric data is used.
