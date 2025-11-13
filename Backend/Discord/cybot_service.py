import os
import re
from typing import Optional, Tuple, List
import httpx

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
DEFAULT_TIMEOUT = 10.0

async def unregister_student(discord_id: str, course_id: str) -> Tuple[bool, str, Optional[str]]:
    """Unregister a student based on the discord_id and course_id"""
    url = f"{API_BASE_URL.rstrip('/')}/students/unregister"
    params = {"discord_id": discord_id, "course_id": course_id}
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            resp = await client.delete(url, params=params)
            if resp.status_code in (200, 201):
                data = resp.json()
                return True, data.get("message", "Registered"), data.get("student_id")
            try:
                return False, resp.json().get("error", resp.text), None
            except Exception:
                return False, resp.text, None
    except httpx.HTTPError as e:
        return False, f"Unregistration error: {e}", None

    
async def split_message(text: str, max_length: int = 1900) -> list:
    """Split text into chunks of max_length characters."""
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    for line in text.split("\n"):
        if len(current_chunk) + len(line) + 1 > max_length:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = line
        else:
            current_chunk += ("\n" if current_chunk else "") + line
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

async def get_student_courses(discord_id: str):
    """Retrieve all courses a student is registered in."""
    url = f"{API_BASE_URL.rstrip('/')}/students/{discord_id}/courses"
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, dict) and "courses" in data:
                    return data["courses"]
            return []
    except httpx.HTTPError:
        return []

async def auto_register_member(member):
    """Auto-register a guild member when they join."""
    guild_name = member.guild.name
    course_id = await get_course_id(guild_name)
    if not course_id:
        print(f"⚠️ Course not found for course {guild_name}")
        return
    
    registered, _ = await is_registered(str(member.id), course_id)
    if registered:
        # print(f"Member {member.display_name} is already registered for course {guild_name}")
        return
    
    success, message, student_id = await register_student(
        str(member.id), member.display_name, course_id
    )
    print(f"Auto-registered {member.display_name}: {message}")

async def get_course_id(guild_name: str) -> Optional[str]:
    """Retrieve the course id by the course name using the API"""
    if not guild_name:
        return None

    url = f"{API_BASE_URL.rstrip('/')}/courses"
    params = {"course_name": guild_name}
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, dict) and "course_id" in data:
                    return data.get("course_id")
                if isinstance(data, list) and len(data) > 0:
                    first = data[0]
                    if isinstance(first, dict) and "course_id" in first:
                        return first.get("course_id")
    except httpx.HTTPError:
        pass
    return None


async def register_student(discord_id: str, name: str, course_id: str) -> Tuple[bool, str, Optional[str]]:
    """Register a student based on the discord_id and course_id"""
    url = f"{API_BASE_URL.rstrip('/')}/students/register"
    params = {"name": name, "discord_id": discord_id, "course_id": course_id}
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            resp = await client.post(url, params=params)
            if resp.status_code in (200, 201):
                data = resp.json()
                return True, data.get("message", "Registered"), data.get("student_id")
            try:
                return False, resp.json().get("error", resp.text), None
            except Exception:
                return False, resp.text, None
    except httpx.HTTPError as e:
        return False, f"Registration error: {e}", None


async def is_registered(discord_id: str, course_id: str) -> Tuple[bool, Optional[str]]:
    """Check if a student is registered for a course using the API"""
    url = f"{API_BASE_URL.rstrip('/')}/students/is_registered"
    params = {"discord_id": discord_id, "course_id": course_id}
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            r = await client.get(url, params=params)
            if r.status_code == 200:
                data = r.json()
                return bool(data.get("registered")), data.get("student_id")
    except httpx.HTTPError:
        pass
    return False, None


async def log_query(student_id: str, course_id: str, query_text: str, response_text: str) -> bool:
    """Log a query to the database via API."""
    url = f"{API_BASE_URL.rstrip('/')}/students/log_query"
    params = {
        "student_id": student_id,
        "course_id": course_id,
        "query_text": query_text,
        "response_text": response_text,
    }
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            resp = await client.post(url, params=params)
            return resp.status_code in (200, 201)
    except httpx.HTTPError:
        return False


async def ask_AI_model(question: str, course_id: str) -> Tuple[str, List[str]]:
    """
    Ask a question about course materials using the RAG pipeline.
    
    Args:
        question (str): The question to ask about the course materials
        course_id (str): UUID of the course to query
    
    Returns:
        Tuple[str, List[str]]: (answer text, list of document sources)
    """
    url = f"{API_BASE_URL.rstrip('/')}/courses/{course_id}/queries"
    params = {"question": question}
    try:
        async with httpx.AsyncClient(timeout=70.0) as client:
            resp = await client.post(url, params=params)
            if resp.status_code != 200:
                return f"⚠️ Backend error ({resp.status_code}): {resp.text}", []
            data = resp.json()

            answer = data.get("answer", "No answer available")
            sources = data.get("sources", [])
            return answer, sources
        
    except httpx.TimeoutException:
        return "⚠️ Request timed out.", []
    except httpx.HTTPError as e:
        return f"Error connecting to backend: {e}", []
