-- ===========================================
-- Database Schema Definition: course_gpt
-- ===========================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- -----------------------------
-- Instructors Table
-- -----------------------------
CREATE TABLE IF NOT EXISTS instructors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    title VARCHAR(150),
    university VARCHAR(150),
    email VARCHAR(150) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------
-- Semesters Table
-- -----------------------------
CREATE TABLE IF NOT EXISTS semesters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(20) UNIQUE NOT NULL
);

INSERT INTO semesters (name)
VALUES ('SPRING'), ('SUMMER'), ('FALL'), ('WINTER')
ON CONFLICT (name) DO NOTHING;

-- -----------------------------
-- Courses Table
-- -----------------------------
CREATE TABLE IF NOT EXISTS courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(150) NOT NULL,
    institution VARCHAR(150) NOT NULL, 
    semester_id INTEGER REFERENCES semesters(id) ON DELETE SET NULL,
    year INTEGER,
    instructor_id UUID REFERENCES instructors(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (name, institution, year, semester_id)
);

-- -----------------------------
-- Documents Table
-- -----------------------------
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_data BYTEA NOT NULL, -- Ideally max ~10MB to keep DB fast; BYTEA can technically hold up to 1GB
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (course_id, file_name)
);

-- -----------------------------
-- Students Table
-- -----------------------------
CREATE TABLE IF NOT EXISTS students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    discord_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------
-- Student-Course Registrations (Many-to-Many)
-- -----------------------------
CREATE TABLE IF NOT EXISTS student_courses (
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, course_id)
);

-- -----------------------------
-- Queries Table (Student ↔ Course)
-- -----------------------------
CREATE TABLE IF NOT EXISTS queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    query_text TEXT NOT NULL,
    response_text TEXT,
    asked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);