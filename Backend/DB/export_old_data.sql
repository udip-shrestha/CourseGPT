-- ===========================================
-- 1. DDL Export (one line per CREATE TABLE)
-- ===========================================
COPY (SELECT 'CREATE TABLE IF NOT EXISTS old_instructors (id UUID, name TEXT, email TEXT, password TEXT, university TEXT, title TEXT, created_at TIMESTAMP, updated_at TIMESTAMP, role_id INT);') TO STDOUT;
COPY (SELECT 'CREATE TABLE IF NOT EXISTS old_courses (id UUID, name TEXT, institution TEXT, year INT, created_at TIMESTAMP, updated_at TIMESTAMP, instructor_id UUID, semester_id INT, rag_strategy_id INT);') TO STDOUT;
COPY (SELECT 'CREATE TABLE IF NOT EXISTS old_documents (id UUID, course_id UUID, file_name TEXT, file_type_id INT, file_data TEXT, uploaded_at TIMESTAMP);') TO STDOUT;
COPY (SELECT 'CREATE TABLE IF NOT EXISTS old_students (id UUID, discord_id TEXT, name TEXT, created_at TIMESTAMP, updated_at TIMESTAMP);') TO STDOUT;
COPY (SELECT 'CREATE TABLE IF NOT EXISTS old_student_courses (student_id UUID, course_id UUID, registered_at TIMESTAMP);') TO STDOUT;
COPY (SELECT 'CREATE TABLE IF NOT EXISTS old_queries (id UUID, student_id UUID, course_id UUID, query_text TEXT, response_text TEXT, asked_at TIMESTAMP);') TO STDOUT;


-- ===========================================
-- 2. INSERT INTO statements (NULL-SAFE)
-- ===========================================

COPY (
    SELECT 'INSERT INTO old_instructors(id, name, email, password, university, title, created_at, updated_at, role_id) VALUES (' ||
           COALESCE(quote_literal(id), 'NULL') || ', ' ||
           COALESCE(quote_literal(name), 'NULL') || ', ' ||
           COALESCE(quote_literal(email), 'NULL') || ', ' ||
           COALESCE(quote_literal(password), 'NULL') || ', ' ||
           COALESCE(quote_literal(university), 'NULL') || ', ' ||
           COALESCE(quote_literal(title), 'NULL') || ', ' ||
           COALESCE(quote_literal(created_at), 'NULL') || ', ' ||
           COALESCE(quote_literal(updated_at), 'NULL') || ', ' ||
           COALESCE(quote_literal(role_id), 'NULL') || ');'
    FROM instructors
) TO STDOUT;

COPY (
    SELECT 'INSERT INTO old_courses(id, name, institution, year, created_at, updated_at, instructor_id, semester_id, rag_strategy_id) VALUES (' ||
           COALESCE(quote_literal(id), 'NULL') || ', ' ||
           COALESCE(quote_literal(name), 'NULL') || ', ' ||
           COALESCE(quote_literal(institution), 'NULL') || ', ' ||
           COALESCE(quote_literal(year), 'NULL') || ', ' ||
           COALESCE(quote_literal(created_at), 'NULL') || ', ' ||
           COALESCE(quote_literal(updated_at), 'NULL') || ', ' ||
           COALESCE(quote_literal(instructor_id), 'NULL') || ', ' ||
           COALESCE(quote_literal(semester_id), 'NULL') || ', ' ||
           COALESCE(quote_literal(rag_strategy_id), 'NULL') || ');'
    FROM courses
) TO STDOUT;

COPY (
    SELECT 'INSERT INTO old_documents(id, course_id, file_name, file_type_id, file_data, uploaded_at) VALUES (' ||
           COALESCE(quote_literal(id), 'NULL') || ', ' ||
           COALESCE(quote_literal(course_id), 'NULL') || ', ' ||
           COALESCE(quote_literal(file_name), 'NULL') || ', ' ||
           COALESCE(quote_literal(file_type_id), 'NULL') || ', ' ||
           COALESCE(quote_literal(encode(file_data, 'hex')), 'NULL') || ', ' ||
           COALESCE(quote_literal(uploaded_at), 'NULL') ||
           ');'
    FROM documents
) TO STDOUT;

COPY (
    SELECT 'INSERT INTO old_students(id, discord_id, name, created_at, updated_at) VALUES (' ||
           COALESCE(quote_literal(id), 'NULL') || ', ' ||
           COALESCE(quote_literal(discord_id), 'NULL') || ', ' ||
           COALESCE(quote_literal(name), 'NULL') || ', ' ||
           COALESCE(quote_literal(created_at), 'NULL') || ', ' ||
           COALESCE(quote_literal(updated_at), 'NULL') ||
           ');'
    FROM students
) TO STDOUT;

COPY (
    SELECT 'INSERT INTO old_student_courses(student_id, course_id, registered_at) VALUES (' ||
           COALESCE(quote_literal(student_id), 'NULL') || ', ' ||
           COALESCE(quote_literal(course_id), 'NULL') || ', ' ||
           COALESCE(quote_literal(registered_at), 'NULL') ||
           ');'
    FROM student_courses
) TO STDOUT;

COPY (
    SELECT 'INSERT INTO old_queries(id, student_id, course_id, query_text, response_text, asked_at) VALUES (' ||
           COALESCE(quote_literal(id), 'NULL') || ', ' ||
           COALESCE(quote_literal(student_id), 'NULL') || ', ' ||
           COALESCE(quote_literal(course_id), 'NULL') || ', ' ||
           COALESCE(quote_literal(query_text), 'NULL') || ', ' ||
           COALESCE(quote_literal(response_text), 'NULL') || ', ' ||
           COALESCE(quote_literal(asked_at), 'NULL') ||
           ');'
    FROM queries
) TO STDOUT;
