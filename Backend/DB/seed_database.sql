-- ===========================================
-- Seed Data for course_gpt
-- ===========================================

-- Ensure pgcrypto is loaded (for gen_random_uuid)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ===========================================
-- Step 1. Insert an Instructor
-- ===========================================
WITH instructor_cte AS (
    INSERT INTO instructors (id, name, title, university, email, password, role_id)
    VALUES (
        gen_random_uuid(),
        'Dr. Sarah Johnson',
        'Associate Professor of Computer Science',
        'Tech University',
        'sarah.johnson@techuni.edu',-- matches fake encryption rule: "encrypt" + password
        '$argon2id$v=19$m=65536,t=3,p=4$AE3fMBD/0KKpaXfT9a2nKQ$sUkLF+lmKJIUXUaokbRJvV2V0KSKdYb8XNJ5j4Jauao',
        (SELECT id FROM instructor_roles WHERE role_name = 'INSTRUCTOR')
    )
    ON CONFLICT (email) DO UPDATE
        SET name = EXCLUDED.name,
            title = EXCLUDED.title,
            university = EXCLUDED.university,
            role_id = EXCLUDED.role_id
    RETURNING id AS instructor_id
),

admin_cte AS (
    INSERT INTO instructors (id, name, title, university, email, password, role_id)
    VALUES (
        gen_random_uuid(),
        'Admin',
        'System Administrator',
        'CourseGPT',
        'course_gpt@admin.edu',
        '$argon2id$v=19$m=65536,t=3,p=4$AE3fMBD/0KKpaXfT9a2nKQ$sUkLF+lmKJIUXUaokbRJvV2V0KSKdYb8XNJ5j4Jauao', 
        (SELECT id FROM instructor_roles WHERE role_name = 'ADMIN')
    )
    ON CONFLICT (email) DO UPDATE
        SET name = EXCLUDED.name,
            title = EXCLUDED.title,
            university = EXCLUDED.university,
            role_id = EXCLUDED.role_id
    RETURNING id AS admin_id
)

SELECT instructor_id, admin_id FROM instructor_cte, admin_cte;