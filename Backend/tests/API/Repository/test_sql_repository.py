import pytest
import uuid
from API.Repository.i_sql_repository import ISQLRepository

# ==========================================================
# FILE TYPES
# ==========================================================
def test_read_file_type_by_mime(repo):
    result = repo.read_file_type_by_mime("application/pdf")

    assert result is not None
    assert result["mime_type"] == "application/pdf"
    assert result["class_name"] == "PDFLoader"


def test_read_all_file_types(repo):
    result = repo.read_all_file_types()

    assert isinstance(result, list)
    assert len(result) >= 2

    mime_types = {r["mime_type"] for r in result}

    assert "application/pdf" in mime_types
    assert "text/plain" in mime_types


# ==========================================================
# RAG STRATEGY
# ==========================================================
def test_read_rag_strategy_by_type(repo):
    # Test SIMPLE strategy lookup (case-insensitive)
    result = repo.read_rag_strategy_by_type("SIMPLE")
    
    assert result is not None
    assert result["type_name"] == "SIMPLE"
    assert result["class_name"] == "SimpleRAGStrategy"
    assert "Basic RAG pipeline" in result["description"]

    # Test case-insensitivity (lowercase)
    result_lower = repo.read_rag_strategy_by_type("simple")

    assert result_lower is not None
    assert result_lower["type_name"] == "SIMPLE"


def test_read_all_rag_strategies(repo):
    results = repo.read_all_rag_strategies()

    assert isinstance(results, list)
    assert len(results) >= 2   # SIMPLE + AGENTIC seeded

    type_names = {r["type_name"] for r in results}

    assert "SIMPLE" in type_names
    assert "AGENTIC" in type_names


# ==========================================================
# DOCUMENTS
# ==========================================================
def test_create_and_read_document(repo, temp_course):
    file_name = "lecture1.pdf"
    file_bytes = b"dummy data"
    file_type_id = 1  # seeded PDF type

    # Create
    doc_id = repo.create_document(temp_course, file_name, file_bytes, file_type_id)
    assert doc_id is not None

    # Read
    doc = repo.read_document(temp_course, doc_id)
    assert doc is not None

    assert doc["file_name"] == file_name
    assert doc["file_data"] == file_bytes
    assert doc["mime_type"] == "application/pdf"  
    assert "can_preview" in doc                 
    assert "native_preview" in doc    


def test_read_all_documents_filters_and_pagination(repo, temp_course):
    for i in range(3):
        repo.create_document(
            temp_course,
            f"file_{i}.pdf",
            b"data" + bytes([i]),
            file_type_id=1
        )

    # Page 1
    page1 = repo.read_all_documents(course_id=temp_course, limit=2, offset=0)
    assert "documents" in page1
    assert page1["total"] >= 3
    assert len(page1["documents"]) == 2

    # Page 2
    page2 = repo.read_all_documents(course_id=temp_course, limit=2, offset=2)
    assert isinstance(page2["documents"], list)
    assert len(page2["documents"]) <= 2

    # File name filter
    filtered = repo.read_all_documents(course_id=temp_course, file_name="file_1")
    names = [d["file_name"] for d in filtered["documents"]]
    assert "file_1.pdf" in names


def test_read_all_documents_filter_by_type(repo, temp_course):
    pdf_id = 1
    txt_id = 2

    repo.create_document(temp_course, "a.pdf", b"1", pdf_id)
    repo.create_document(temp_course, "b.txt", b"2", txt_id)

    # PDF filter
    pdf_docs = repo.read_all_documents(course_id=temp_course, file_type_id=pdf_id)
    assert len(pdf_docs["documents"]) == 1
    for d in pdf_docs["documents"]:
        assert d["file_name"].endswith(".pdf")

    # TXT filter
    txt_docs = repo.read_all_documents(course_id=temp_course, file_type_id=txt_id)
    for d in txt_docs["documents"]:
        assert d["file_name"].endswith(".txt")


def test_delete_document(repo, temp_course):
    doc_id = repo.create_document(temp_course, "temp.txt", b"hello", file_type_id=2)
    assert repo.read_document(temp_course, doc_id) is not None

    repo.delete_document(temp_course, doc_id)
    assert repo.read_document(temp_course, doc_id) is None


def test_update_document_processing_status_completed(repo, temp_course):
    # Create a new document (initial status = PROCESSING)
    doc_id = repo.create_document(temp_course, "complete_test.pdf", b"x", file_type_id=1)

    # Update to COMPLETED
    repo.update_document_processing_status_completed(doc_id)

    # Read the full record using read_all_documents
    res = repo.read_all_documents(course_id=temp_course, file_name="complete_test")
    assert len(res["documents"]) == 1

    doc = res["documents"][0]
    assert doc["processing_status"] == "COMPLETED"


def test_update_document_processing_status_failed(repo, temp_course):
    # Create a new document (initial status = PROCESSING)
    doc_id = repo.create_document(temp_course, "failed_test.pdf", b"y", file_type_id=1)

    # Update to FAILED
    repo.update_document_processing_status_failed(doc_id)

    # Read using read_all_documents
    res = repo.read_all_documents(course_id=temp_course, file_name="failed_test")
    assert len(res["documents"]) == 1

    doc = res["documents"][0]
    assert doc["processing_status"] == "FAILED"


# ==========================================================
# INSTRUCTORS
# ==========================================================
def test_create_instructor(repo: ISQLRepository):
    """Should create instructor and reject duplicates/invalid data."""
    instructor_id = repo.create_instructor("Dr. Jane Smith", "Professor", "ISU", "jane.smith@isu.edu", "hash")
    assert instructor_id is not None

    # Duplicate email → should fail (unique constraint)
    with pytest.raises(Exception): repo.create_instructor("Copy", "Prof", "ISU", "jane.smith@isu.edu", "hash2")

    # Empty fields → check constraints fail
    with pytest.raises(Exception): repo.create_instructor("", "", "", "unique@isu.edu", "pw")


def test_read_instructor(repo: ISQLRepository):
    """Should fetch instructor by ID and email."""
    iid = repo.create_instructor("Dr. Jane Smith", "Professor", "ISU", "jane.smith@isu.edu", "hash")

    inst = repo.read_instructor(iid)
    assert inst and inst["name"] == "Dr. Jane Smith" and inst["role"] == "INSTRUCTOR"

    inst_by_email = repo.read_instructor_by_email("jane.smith@isu.edu")
    assert inst_by_email and inst_by_email["email"] == "jane.smith@isu.edu"

    # Not found
    assert repo.read_instructor("00000000-0000-0000-0000-000000000000") is None
    assert repo.read_instructor_by_email("none@isu.edu") is None


def test_read_all_instructors_features(repo: ISQLRepository, temp_instructor: str):
    """Should support filtering, ordering, and pagination."""
    data = repo.read_all_instructors()
    assert isinstance(data["instructors"], list)

    # Filtering by role_id (INSTRUCTOR)
    filtered = repo.read_all_instructors(role=2)["instructors"]  # 2 = INSTRUCTOR from seed
    assert all(inst["role_id"] == 2 for inst in filtered)

    # Pagination
    limited = repo.read_all_instructors(limit=1)["instructors"]
    assert len(limited) <= 1

    # Invalid order_by → fallback, but still returns list
    invalid_order = repo.read_all_instructors(order_by="does_not_exist")["instructors"]
    assert isinstance(invalid_order, list)

    # Filtering by name
    by_name = repo.read_all_instructors(name="Dr")["instructors"]
    assert all("dr" in inst["name"].lower() for inst in by_name)


def test_update_instructor(repo: ISQLRepository):
    """Should update instructor fields dynamically."""
    iid = repo.create_instructor("Old Name", "Old Title", "ISU", "old@isu.edu", "hash")
    updated = repo.update_instructor(iid, {"name": "New Name", "title": "New Title"})
    assert updated["name"] == "New Name" and updated["title"] == "New Title"

    # Invalid ID should return None
    assert repo.update_instructor("00000000-0000-0000-0000-000000000000", {"name": "X"}) is None


def test_delete_instructor(repo: ISQLRepository):
    """Should delete an instructor safely."""
    iid = repo.create_instructor("Dr. John Doe", "Lecturer", "MIT", "john.doe@mit.edu", "hash")
    assert repo.read_instructor(iid) is not None

    repo.delete_instructor(iid)
    assert repo.read_instructor(iid) is None

    # Re-delete should not crash
    repo.delete_instructor(iid)


# ==========================================================
# COURSES
# ==========================================================
def test_create_and_read_course(repo, temp_instructor):
    course_id = repo.create_course(
        instructor_id=temp_instructor,
        name="Test Course",
        institution="ISU",
        semester_id=1,
        year=2025
    )
    assert course_id is not None

    course = repo.read_course(course_id)
    assert course and course["name"] == "Test Course" and course["institution"] == "ISU"


def test_read_all_courses_basic(repo):
    courses = repo.read_all_courses()["courses"]
    assert isinstance(courses, list)


def test_read_all_courses_filters(repo, temp_instructor):
    # Insert two different courses
    cid1 = repo.create_course(temp_instructor, "A Course", "ISU", 1, 2025)
    cid2 = repo.create_course(temp_instructor, "B Course", "MIT", 2, 2024)

    # Filter by name
    by_name = repo.read_all_courses(name="A")["courses"]
    assert all("a" in c["name"].lower() for c in by_name)

    # Filter by instructor
    by_instructor = repo.read_all_courses(instructor_id=temp_instructor)["courses"]
    assert all(str(c["instructor_id"]) == temp_instructor for c in by_instructor)

    # Filter by semester
    by_semester = repo.read_all_courses(semester_id=1)["courses"]
    assert all(c["semester_id"] == 1 for c in by_semester)

    # Filter by institution
    by_inst = repo.read_all_courses(institution="ISU")["courses"]
    assert all("isu" in c["institution"].lower() for c in by_inst)


def test_read_all_courses_invalid_order_by(repo):
    result = repo.read_all_courses(order_by="bad_field")["courses"]
    assert isinstance(result, list)  # Should fallback to created_at ordering


def test_read_all_courses_pagination(repo, temp_instructor):
    # Insert multiple courses
    for i in range(4):
        repo.create_course(
            instructor_id=temp_instructor, name=f"Course{i}",
            institution="ISU", semester_id=1, year=2020 + i
        )

    first_page = repo.read_all_courses(limit=2, offset=0)["courses"]
    second_page = repo.read_all_courses(limit=2, offset=2)["courses"]

    assert len(first_page) <= 2
    assert len(second_page) <= 2
    assert first_page != second_page  # pagination should differ


def test_update_course(repo, temp_instructor):
    cid = repo.create_course(temp_instructor, "OldName", "ISU", 1, 2023)
    updated = repo.update_course(cid, {"name": "NewName", "institution": "MIT"})
    assert updated["name"] == "NewName" and updated["institution"] == "MIT"


def test_get_course_by_name(repo, temp_instructor):
    name = "UniqueCourse"
    cid = repo.create_course(temp_instructor, name, "ISU", 1, 2025)
    course = repo.get_course_by_name(name)

    assert course and course["name"] == name and course["institution"] == "ISU"


def test_delete_course(repo, temp_instructor):
    cid = repo.create_course(temp_instructor, "Temp Course", "ISU", 1, 2025)
    assert repo.read_course(cid) is not None

    repo.delete_course(cid)
    assert repo.read_course(cid) is None

    # Re-delete should not crash
    repo.delete_course(cid)


def test_read_course_by_name(repo, temp_instructor):
    """Should return only the course with matching name + instructor_id."""
    
    cid = repo.create_course(temp_instructor, "Algorithms", "ISU", 1, 2025)
    other_inst = repo.create_instructor("John Doe", "Professor", "MIT", "john@test.com", "pass")
    repo.create_course(other_inst, "Algorithms", "MIT", 1, 2024)

    course = repo.read_course_by_name("Algorithms", temp_instructor)
    assert course and str(course["id"]) == cid and str(course["instructor_id"]) == temp_instructor

    assert repo.read_course_by_name("Algorithms", "00000000-0000-0000-0000-000000000000") is None


# ==========================================================
# STUDENTS
# ==========================================================
def test_create_and_read_student(repo, temp_course):
    student_name = "Alice"
    discord_id = "alice123"
    student_id = repo.create_student(student_name, discord_id, temp_course)
    assert student_id is not None

    student = repo.read_student(student_id)
    assert student is not None
    assert student["name"] == student_name
    assert student["course_id"] == uuid.UUID(temp_course)


def test_create_student_existing_discord(repo, temp_course):
    discord_id = "repeat123"
    student1 = repo.create_student("Student1", discord_id, temp_course)
    student2 = repo.create_student("Student1", discord_id, temp_course)
    assert student1 == student2  # Should reuse same student_id


def test_read_all_students(repo, temp_course):
    repo.create_student("Bob", "bob123", temp_course)
    all_students = repo.read_all_students()
    assert isinstance(all_students, list)
    course_students = repo.read_all_students(temp_course)
    assert isinstance(course_students, list)


def test_read_student_by_discord(repo, temp_course):
    discord_id = "disc999"
    repo.create_student("Cathy", discord_id, temp_course)
    student = repo.read_student_by_discord(discord_id)
    assert student is not None
    assert student["discord_id"] == discord_id


def test_read_courses_by_discord(repo, temp_course):
    discord_id = "linked123"
    repo.create_student("David", discord_id, temp_course)
    courses = repo.read_courses_by_discord(discord_id)
    assert isinstance(courses, list)
    assert any("course_name" in c for c in courses)


def remove_student_from_course(self, student_id, course_id) -> bool:
    with self.connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM course_student WHERE student_id = %s AND course_id = %s",
            (student_id, course_id),
        )
        self.connection.commit()
        # Return True if any rows were deleted, False otherwise
        return cursor.rowcount > 0


# ==========================================================
# QUERIES (Student Questions)
# ==========================================================
def test_create_and_read_query(repo, temp_course, temp_student):
    """Should create a query and read it back correctly."""
    qid = repo.create_query(
        student_id=temp_student,
        course_id=temp_course,
        query_text="What is runtime?",
        response_text="O(n)."
    )
    assert qid is not None

    q = repo.read_query(temp_course, qid)
    assert q and q["query_text"] == "What is runtime?" and q["response_text"] == "O(n)."


def test_read_queries_for_student_course(repo, temp_course, temp_student):
    """Should filter, sort, and paginate student–course queries."""
    for i in range(3):
        repo.create_query(temp_student, temp_course, f"Q{i}", f"A{i}")

    results = repo.read_queries_for_student_course(
        student_id=temp_student,
        course_id=temp_course,
        limit=2,
        offset=0
    )["queries"]
    assert len(results) == 2

    # Check fallback ordering works
    bad_order = repo.read_queries_for_student_course(
        temp_student, temp_course, order_by="invalid"
    )["queries"]
    assert isinstance(bad_order, list)


def test_read_all_queries_for_course(repo, temp_course, temp_student):
    """Should fetch all queries for a course with pagination and sorting."""
    for i in range(3):
        repo.create_query(temp_student, temp_course, f"Q{i}", f"A{i}")

    first_page = repo.read_all_queries_for_course(
        course_id=temp_course,
        limit=2,
        offset=0
    )["queries"]
    assert len(first_page) == 2

    second_page = repo.read_all_queries_for_course(
        course_id=temp_course,
        limit=2,
        offset=2
    )["queries"]
    assert len(second_page) >= 0
    assert first_page != second_page  # pages should differ


def test_delete_query(repo, temp_course, temp_student):
    """Should delete a query and handle repeated deletion safely."""
    qid = repo.create_query(temp_student, temp_course, "Will it delete?", "Yes.")
    assert repo.read_query(temp_course, qid) is not None

    repo.delete_query(temp_course, qid)
    assert repo.read_query(temp_course, qid) is None

    # Re-delete should not raise
    repo.delete_query(temp_course, qid)

