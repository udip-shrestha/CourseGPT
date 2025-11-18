SET client_min_messages = WARNING;

-------------------------------------------------------
-- 1. instructor_roles
-------------------------------------------------------
INSERT INTO instructor_roles(id, role_name)
SELECT id, role_name
FROM old_instructor_roles
WHERE role_name IS NOT NULL AND trim(role_name) <> ''
ON CONFLICT (id) DO NOTHING;

-------------------------------------------------------
-- 2. instructors
-------------------------------------------------------
INSERT INTO instructors (
    id, name, email, password, university, title,
    created_at, updated_at, role_id
)
SELECT
    id,
    name,
    email,
    password,
    university,
    title,
    created_at,
    COALESCE(updated_at, created_at),
    role_id
FROM old_instructors
WHERE 
    id IS NOT NULL
    AND name IS NOT NULL AND trim(name) <> ''
    AND email IS NOT NULL AND trim(email) <> ''
    AND password IS NOT NULL AND trim(password) <> ''
    AND university IS NOT NULL AND trim(university) <> ''
    AND title IS NOT NULL AND trim(title) <> ''
ON CONFLICT (id) DO NOTHING;

-------------------------------------------------------
-- 3. semesters
-------------------------------------------------------
INSERT INTO semesters(id, name)
SELECT id, name
FROM old_semesters
WHERE name IS NOT NULL AND trim(name) <> ''
ON CONFLICT (id) DO NOTHING;

-------------------------------------------------------
-- 4. courses (NO rag_strategy_id)
-------------------------------------------------------
INSERT INTO courses (
    id, name, institution, year,
    created_at, updated_at,
    instructor_id, semester_id
)
SELECT
    c.id,
    c.name,
    c.institution,
    c.year,
    c.created_at,
    c.created_at AS updated_at,
    c.instructor_id,
    c.semester_id
FROM old_courses c
WHERE
    c.id IS NOT NULL
    AND trim(c.name) <> ''
    AND trim(c.institution) <> ''
    AND c.year IS NOT NULL AND c.year >= 0
    AND c.instructor_id IN (SELECT id FROM instructors)
    AND c.semester_id IN (SELECT id FROM semesters)
ON CONFLICT (id) DO NOTHING;

-------------------------------------------------------
-- 5. file_types
-------------------------------------------------------
INSERT INTO file_types(id, mime_type, extension)
SELECT id, mime_type, extension
FROM old_file_types
WHERE 
    trim(mime_type) <> '' 
    AND trim(extension) <> ''
ON CONFLICT (id) DO NOTHING;

-------------------------------------------------------
-- 6. documents
-------------------------------------------------------
INSERT INTO documents (
    id, course_id, file_name, file_type_id, file_data, uploaded_at
)
SELECT
    id,
    course_id,
    file_name,
    file_type_id,
    decode(file_data, 'hex'),
    uploaded_at
FROM old_documents
WHERE
    id IS NOT NULL
    AND trim(file_name) <> ''
    AND course_id IN (SELECT id FROM courses)
    AND file_type_id IN (SELECT id FROM file_types)
ON CONFLICT (id) DO NOTHING;

-------------------------------------------------------
-- 7. students
-------------------------------------------------------
INSERT INTO students(id, discord_id, name, created_at, updated_at)
SELECT
    id,
    NULLIF(trim(discord_id), ''),
    name,
    created_at,
    created_at
FROM old_students
WHERE
    id IS NOT NULL
    AND trim(name) <> ''
ON CONFLICT (id) DO NOTHING;

-------------------------------------------------------
-- 8. student_courses
-------------------------------------------------------
INSERT INTO student_courses(student_id, course_id, registered_at)
SELECT
    student_id, course_id, registered_at
FROM old_student_courses
WHERE
    student_id IN (SELECT id FROM students)
    AND course_id IN (SELECT id FROM courses)
ON CONFLICT DO NOTHING;

-------------------------------------------------------
-- 9. queries
-------------------------------------------------------
INSERT INTO queries (
    id, student_id, course_id, query_text, response_text, asked_at
)
SELECT
    id,
    CASE WHEN student_id IN (SELECT id FROM students) THEN student_id ELSE NULL END,
    course_id,
    query_text,
    response_text,
    asked_at
FROM old_queries
WHERE
    id IS NOT NULL
    AND course_id IN (SELECT id FROM courses)
    AND trim(query_text) <> ''
ON CONFLICT (id) DO NOTHING;

-------------------------------------------------------
-- 10. Set migrated courses to SIMPLE rag strategy
-------------------------------------------------------
UPDATE courses
SET rag_strategy_id = (
    SELECT id FROM rag_strategies WHERE type_name = 'SIMPLE'
)
WHERE rag_strategy_id IS NULL;
