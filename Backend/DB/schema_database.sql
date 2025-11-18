-- ===========================================
-- Database Schema Definition: course_gpt
-- ===========================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- -----------------------------
-- Instructors Table
-- -----------------------------
CREATE TABLE IF NOT EXISTS instructor_roles (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL
);

INSERT INTO instructor_roles (role_name)
VALUES 
    ('ADMIN'), 
    ('INSTRUCTOR')
ON CONFLICT (role_name) DO NOTHING;

CREATE TABLE IF NOT EXISTS instructors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL CHECK (trim(name) <> ''),
    email VARCHAR(150) UNIQUE NOT NULL CHECK (trim(email) <> ''),
    password TEXT NOT NULL CHECK (trim(password) <> ''),
    university VARCHAR(150) NOT NULL CHECK (trim(university) <> ''),
    title VARCHAR(100) NOT NULL CHECK (trim(title) <> ''),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    role_id INTEGER REFERENCES instructor_roles(id) ON DELETE SET NULL
);

-- -----------------------------
-- Semesters Table
-- -----------------------------
CREATE TABLE IF NOT EXISTS semesters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(20) UNIQUE NOT NULL
);

INSERT INTO semesters (name)
VALUES 
    ('SPRING'), 
    ('SUMMER'), 
    ('FALL'), 
    ('WINTER')
ON CONFLICT (name) DO NOTHING;

-- -----------------------------
-- RAG Strategies Table
-- -----------------------------
CREATE TABLE IF NOT EXISTS rag_strategies (
    id SERIAL PRIMARY KEY,
    type_name VARCHAR(50) UNIQUE NOT NULL,
    class_name VARCHAR(100) NOT NULL,
    description TEXT
);

INSERT INTO rag_strategies (type_name, class_name, description)
VALUES
    ('SIMPLE', 'SimpleRAGStrategy', 'Basic RAG pipeline: retrieve → build prompt → generate'),
    ('AGENTIC', 'AgenticRAGStrategy', 'Agentic RAG using tools and multi-step reasoning')
ON CONFLICT (type_name) DO NOTHING;

-- -----------------------------
-- Courses Table
-- -----------------------------
CREATE TABLE IF NOT EXISTS courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(150) NOT NULL CHECK (trim(name) <> ''),
    institution VARCHAR(150) NOT NULL CHECK (trim(institution) <> ''),
    year INTEGER NOT NULL CHECK (year >= 0),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    instructor_id UUID NOT NULL REFERENCES instructors(id) ON DELETE CASCADE,
    semester_id INTEGER NOT NULL REFERENCES semesters(id) ON DELETE RESTRICT,
    rag_strategy_id INT REFERENCES rag_strategies(id) ON DELETE SET NULL
);

-- -----------------------------
-- File Types Table
-- -----------------------------
CREATE TABLE IF NOT EXISTS file_types (
    id SERIAL PRIMARY KEY,
    mime_type VARCHAR(100) UNIQUE NOT NULL,   -- e.g. 'application/pdf'
    extension VARCHAR(10) UNIQUE NOT NULL     -- e.g. 'pdf'
);

INSERT INTO file_types (mime_type, extension)
VALUES
    ('application/pdf', 'pdf'),
    ('text/plain', 'txt')
ON CONFLICT (mime_type) DO NOTHING;

-- -----------------------------
-- Documents Table
-- -----------------------------
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_type_id INT REFERENCES file_types(id) ON DELETE RESTRICT,
    file_data BYTEA NOT NULL, -- Ideally max ~10MB to keep DB fast; BYTEA can technically hold up to 1GB
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (course_id, file_name)
);

-- -----------------------------
-- Students Table
-- -----------------------------
CREATE TABLE IF NOT EXISTS students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    discord_id VARCHAR(50) UNIQUE CHECK (discord_id IS NULL OR trim(discord_id) <> ''),
    name VARCHAR(100) NOT NULL CHECK (trim(name) <> ''),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------
-- Student-Course Registrations (Many-to-Many)
-- -----------------------------
CREATE TABLE IF NOT EXISTS student_courses (
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    registered_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, course_id)
);

-- -----------------------------
-- Queries Table (Student ↔ Course)
-- -----------------------------
CREATE TABLE IF NOT EXISTS queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE SET NULL,
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    query_text TEXT NOT NULL,
    response_text TEXT,
    asked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);