-- ===========================================
-- Seed Data for course_gpt
-- ===========================================

-- Ensure pgcrypto is loaded (for gen_random_uuid)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ===========================================
-- Step 1. Insert an Instructor
-- ===========================================
WITH instructor_cte AS (
    INSERT INTO instructors (id, name, title, university, email)
    VALUES (
        gen_random_uuid(),
        'Dr. Sarah Johnson',
        'Associate Professor of Computer Science',
        'Tech University',
        'sarah.johnson@techuni.edu'
    )
    ON CONFLICT (email) DO UPDATE
        SET name = EXCLUDED.name
    RETURNING id AS instructor_id
),

-- ===========================================
-- Step 2. Insert a Course linked to Instructor & Semester
-- ===========================================
course_cte AS (
    INSERT INTO courses (id, name, institution, semester_id, year, instructor_id)
    VALUES (
        gen_random_uuid(),
        'Data Structures',
        'Iowa State University',
        (SELECT id FROM semesters WHERE name = 'FALL'),
        2025,
        (SELECT instructor_id FROM instructor_cte)
    )
    ON CONFLICT (name, institution, year, semester_id) DO UPDATE
        SET instructor_id = EXCLUDED.instructor_id
    RETURNING id AS course_id
)

-- ===========================================
-- Step 3. Insert a Document linked to Course
-- ===========================================
INSERT INTO documents (id, course_id, file_name, file_data)
SELECT
    gen_random_uuid(),
    course_cte.course_id,
    'Backend_Knowledge.pdf',
    pg_read_binary_file('course_gpt/Backend_Knowledge.pdf')
FROM course_cte
ON CONFLICT (course_id, file_name) DO UPDATE
    SET file_data = EXCLUDED.file_data,
        uploaded_at = NOW();


-- ===========================================
-- Step 4. Insert Students
-- ===========================================
INSERT INTO students (id, discord_id, name)
VALUES
    (gen_random_uuid(), 'disc_001', 'John Doe'),
    (gen_random_uuid(), 'disc_002', 'Jane Smith')
ON CONFLICT (discord_id) DO UPDATE
    SET name = EXCLUDED.name;

-- ===========================================
-- Step 5. Register Students in the Course
-- ===========================================
INSERT INTO student_courses (student_id, course_id)
SELECT s.id, c.id
FROM students s
CROSS JOIN courses c
WHERE s.discord_id IN ('disc_001', 'disc_002')
  AND c.name = 'Data Structures'
ON CONFLICT DO NOTHING;

-- ===========================================
-- Step 6. Seed Queries for Each Student
-- ===========================================
INSERT INTO queries (id, student_id, course_id, query_text, response_text)
SELECT
    gen_random_uuid(),
    s.id,
    c.id,
    'What is the difference between an array and a linked list?',
    'Arrays store elements in contiguous memory while linked lists use nodes connected by pointers.'
FROM students s
JOIN courses c ON c.name = 'Data Structures'
WHERE s.discord_id = 'disc_001'
ON CONFLICT DO NOTHING;