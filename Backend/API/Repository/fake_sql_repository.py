from typing import Optional, List, Dict, Any
import uuid
import datetime

from API.Repository.i_sql_repository import ISQLRepository


class FakeSQLRepository(ISQLRepository):
    """
    In-memory mock implementation of ISQLRepository.

    Simulates database tables and relationships entirely in Python.
    Useful for unit tests of Service Layer or local development without a live DB.
    """

    def __init__(self):
        # --------------------------
        # In-memory “tables”
        # --------------------------
        self.instructors: List[Dict[str, Any]] = []
        self.semesters: List[Dict[str, Any]] = []
        self.courses: List[Dict[str, Any]] = []
        self.file_types: List[Dict[str, Any]] = []
        self.documents: List[Dict[str, Any]] = []

        # --------------------------
        # Seed data
        # --------------------------
        self._seed_instructors()
        self._seed_semesters()
        self._seed_file_types()
        self._seed_courses()



    # ======================================================
    # SEEDING HELPERS
    # ======================================================
    def _seed_instructors(self) -> None:
        """Seed example instructors."""
        self.instructors = [
            {
                "id": str(uuid.uuid4()),
                "name": "Dr. Ada Lovelace",
                "title": "Professor",
                "university": "Iowa State University",
                "email": "ada@example.edu",
                "created_at": datetime.datetime.now(datetime.UTC),
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Dr. Alan Turing",
                "title": "Associate Professor",
                "university": "Iowa State University",
                "email": "alan@example.edu",
                "created_at": datetime.datetime.now(datetime.UTC),
            },
        ]
        
    def _seed_semesters(self) -> None:
        """Initialize semester records."""
        semester_names = ["SPRING", "SUMMER", "FALL", "WINTER"]
        self.semesters = [{"id": i + 1, "name": name} for i, name in enumerate(semester_names)]

    def _seed_file_types(self) -> None:
        """Initialize default file types."""
        self.file_types.extend([
            {"id": 1, "mime_type": "application/pdf", "extension": "pdf"},
            {"id": 2, "mime_type": "text/plain", "extension": "txt"},
        ])

    def _seed_courses(self) -> None:
        """Seed example courses."""
        instructor_id = self.instructors[0]["id"]
        semester_id = next((s["id"] for s in self.semesters if s["name"] == "FALL"), 3)
        self.courses.append({
            "id": str(uuid.uuid4()),
            "name": "CPRE 230",
            "institution": "Iowa State University",
            "semester_id": semester_id,
            "year": 2025,
            "instructor_id": instructor_id,
            "created_at": datetime.datetime.now(datetime.UTC),
        })
        self.courses.append({
            "id": str(uuid.uuid4()),
            "name": "COM S 319",
            "institution": "Iowa State University",
            "semester_id": semester_id,
            "year": 2025,
            "instructor_id": instructor_id,
            "created_at": datetime.datetime.now(datetime.UTC),
        })



    # ======================================================
    # INTERNAL HELPERS
    # ======================================================
    def _semester_exists(self, semester_id: int) -> bool:
        return any(s["id"] == semester_id for s in self.semesters)

    def _instructor_exists(self, instructor_id: str) -> bool:
        return any(i["id"] == instructor_id for i in self.instructors)

    def _file_type_exists(self, file_type_id: int) -> bool:
        return any(ft["id"] == file_type_id for ft in self.file_types)

    def _course_exists(self, course_id: str) -> bool:
        return any(c["id"] == course_id for c in self.courses)



    # ======================================================
    # FILE TYPES
    # ======================================================
    def read_file_type_by_mime(self, mime_type: str) -> Optional[Dict[str, Any]]:
        return next((ft for ft in self.file_types if ft["mime_type"] == mime_type), None)

    def read_file_type_by_extension(self, extension: str) -> Optional[Dict[str, Any]]:
        return next((ft for ft in self.file_types if ft["extension"] == extension), None)

    def read_all_file_types(self) -> List[Dict[str, Any]]:
        return self.file_types.copy()



    # ======================================================
    # DOCUMENTS
    # ======================================================
    def create_document(
        self,
        course_id: str,
        file_name: str,
        file_bytes: bytes,
        file_type_id: int
    ) -> str:
        # FK constraints
        if not self._course_exists(course_id):
            raise ValueError(f"course_id={course_id} does not exist.")
        if not self._file_type_exists(file_type_id):
            raise ValueError(f"file_type_id={file_type_id} does not exist.")

        # UNIQUE (course_id, file_name)
        if any(d["course_id"] == course_id and d["file_name"] == file_name for d in self.documents):
            raise ValueError(f"Duplicate (course_id, file_name): ({course_id}, {file_name})")

        doc_id = str(uuid.uuid4())
        self.documents.append({
            "id": doc_id,
            "course_id": course_id,
            "file_name": file_name,
            "file_data": file_bytes,
            "file_type_id": file_type_id,
            "uploaded_at": datetime.datetime.now(datetime.UTC),
        })
        return doc_id

    def read_document(self, doc_id: str) -> Optional[dict]:
        return next((doc for doc in self.documents if doc["id"] == doc_id), None)

    def delete_document(self, doc_id: str) -> None:
        self.documents = [doc for doc in self.documents if doc["id"] != doc_id]

    def read_all_documents(
        self,
        course_id: str,
        file_type_id: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
        order_by: str = "uploaded_at",
        order_dir: str = "desc",
    ) -> List[dict]:
        # Filter by course_id (required)
        results = [d for d in self.documents if d.get("course_id") == course_id]


        # Apply filters
        if file_type_id:
            results = [d for d in results if d["file_type_id"] == file_type_id]

        # Sort results
        reverse = order_dir.lower() == "desc"
        results.sort(key=lambda d: d.get(order_by, None), reverse=reverse)

        # Pagination
        return results[offset: offset + limit]
