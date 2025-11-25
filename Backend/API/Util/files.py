import os
import tempfile
import uuid
from unstructured.partition.auto import partition
from contextlib import contextmanager


@contextmanager
def create_temp_file_from_bytes(file_name: str, file_bytes: bytes):
    """
    Create a temporary file using <uuid>_<original_filename>.
    Example:
        /tmp/91c2f8e4f1c54ab7a12d_lecture_notes.docx
    """
    temp_path = None

    try:
        temp_dir = tempfile.gettempdir()
        # Preserve full original filename (keeps extension!)
        temp_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}_{file_name}")

        with open(temp_path, "wb") as f:
            f.write(file_bytes)

        yield temp_path

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


def convert_to_html(file_bytes: bytes, file_name: str) -> str:
    """
    Converts DOCX, PPTX, XLSX etc. into HTML using Unstructured to allow for previewing.
    """
    with create_temp_file_from_bytes(file_name, file_bytes) as temp_path:
        elements = partition(filename=temp_path)

    # Convert elements to HTML
    html_parts = []
    for el in elements:
        try:
            html_parts.append(el.to_html())
        except Exception:
            html_parts.append(str(el))

    return "<br>".join(html_parts)


def convert_to_html_bytes(file_bytes: bytes, file_name: str) -> bytes:
    """
    Converts input file bytes to HTML bytes.
    """
    html_str = convert_to_html(file_bytes, file_name)
    return html_str.encode("utf-8")
