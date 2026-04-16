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
    rag_strategy_id INT REFERENCES rag_strategies(id) ON DELETE SET NULL,
    -- Canvas integration
    canvas_course_id VARCHAR(100) UNIQUE,
    canvas_context_id VARCHAR(255) UNIQUE
);

-- -----------------------------
-- File Types Table
-- -----------------------------
CREATE TABLE IF NOT EXISTS file_types (
    id SERIAL PRIMARY KEY,
    mime_type VARCHAR(100) UNIQUE NOT NULL,   -- e.g. 'application/pdf'
    class_name VARCHAR(100) NOT NULL,
    native_preview BOOLEAN NOT NULL,
    can_preview BOOLEAN NOT NULL 
);

INSERT INTO file_types (mime_type, class_name, native_preview, can_preview)
VALUES
    -- PDF
    ('application/pdf', 'PDFLoader', TRUE, TRUE),

    -- TXT
    ('text/plain', 'TXTLoader', TRUE, TRUE),
    ('application/octet-stream', 'TXTLoader', FALSE, TRUE),

    -- Markdown
    ('text/markdown', 'MDLoader', FALSE, TRUE),
    ('text/x-markdown', 'MDLoader', FALSE, TRUE),
    ('application/markdown', 'MDLoader', FALSE, TRUE),

    -- HTML
    ('text/html', 'HTMLLoader', TRUE, TRUE),
    ('application/xhtml+xml', 'HTMLLoader', TRUE, TRUE),

    -- XML
    ('application/xml', 'XMLLoader', TRUE, TRUE),
    ('text/xml', 'XMLLoader', TRUE, TRUE),
    ('application/x-xml', 'XMLLoader', TRUE, TRUE),

    -- CSV
    ('text/csv', 'CSVLoader', FALSE, TRUE),
    ('application/csv', 'CSVLoader', FALSE, TRUE),
    ('text/x-comma-separated-values', 'CSVLoader', FALSE, TRUE),

    -- Word
    ('application/msword', 'DOCXLoader', FALSE, FALSE),
    ('application/x-msword', 'DOCXLoader', FALSE, FALSE),
    ('application/vnd.ms-word', 'DOCXLoader', FALSE, FALSE),
    ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'DOCXLoader', FALSE, FALSE),

    -- Excel
    ('application/vnd.ms-excel', 'XLSXLoader', FALSE, FALSE),
    ('application/msexcel', 'XLSXLoader', FALSE, FALSE),
    ('application/x-msexcel', 'XLSXLoader', FALSE, FALSE),
    ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'XLSXLoader', FALSE, FALSE),

    -- PowerPoint
    ('application/vnd.ms-powerpoint', 'PPTXLoader', FALSE, FALSE),
    ('application/mspowerpoint', 'PPTXLoader', FALSE, FALSE),
    ('application/x-mspowerpoint', 'PPTXLoader', FALSE, FALSE),
    ('application/vnd.openxmlformats-officedocument.presentationml.presentation', 'PPTXLoader', FALSE, FALSE),

    -- Images
    ('image/png', 'ImageLoader', TRUE, TRUE),
    ('image/jpeg', 'ImageLoader', TRUE, TRUE),
    ('image/jpg', 'ImageLoader', TRUE, TRUE)
ON CONFLICT (mime_type) DO NOTHING;

-- -----------------------------
-- Processing Status Table
-- -----------------------------
CREATE TABLE IF NOT EXISTS processing_statuses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(20) NOT NULL UNIQUE
);

INSERT INTO processing_statuses (name)
VALUES 
    ('PROCESSING'),
    ('COMPLETED'),
    ('FAILED')
ON CONFLICT (name) DO NOTHING;

-- -----------------------------
-- Documents Table
-- -----------------------------
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL CHECK (trim(file_name) <> ''),
    file_type_id INT NOT NULL REFERENCES file_types(id) ON DELETE RESTRICT,
    processing_status_id INT NOT NULL REFERENCES processing_statuses(id) ON DELETE RESTRICT,
    file_data BYTEA NOT NULL,
    uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
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
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    -- Canvas integration
    canvas_user_id VARCHAR(100) UNIQUE
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

-- ----------------------------------------------
-- Feedback table
-- Stores student-submitted feedback for a course
-- ----------------------------------------------
CREATE TABLE IF NOT EXISTS feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    feedback_text TEXT NOT NULL,
    received_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------
-- Answer Feedback table
-- Stores feedback for AI-generated answers
-- ----------------------------------------------
CREATE TABLE IF NOT EXISTS answer_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_id UUID NOT NULL,
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    student_id TEXT NOT NULL,
    vote TEXT CHECK (vote IN ('up', 'down')) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (query_id, student_id)
);

-- -----------------------------
-- Password Reset Codes Table
-- -----------------------------
CREATE TABLE IF NOT EXISTS password_reset_codes (
    instructor_id UUID PRIMARY KEY REFERENCES instructors(id) ON DELETE CASCADE,
    code TEXT NOT NULL CHECK (code ~ '^[0-9]{6}$'),
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------
-- Discord Admins Table
-- -----------------------------
CREATE TABLE IF NOT EXISTS discord_admins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    discord_id TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
