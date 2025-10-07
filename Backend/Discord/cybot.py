import discord
import requests
import json
import os
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import uuid
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")
H_MODEL = "deepset/roberta-base-squad2"

STUDENTS_FILE = "students.json"
QUERIES_FILE = "queries.json"

# Load JSON data
def load_json(filename):
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            json.dump({"students": []} if "students" in filename else {"queries": []}, f)
    with open(filename, "r") as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

# Check registration
def is_registered(discord_id, course_id):
    data = load_json(STUDENTS_FILE)
    for student in data["students"]:
        if student["discord_id"] == str(discord_id):
            for course in student["courses"]:
                if course["course_id"] == course_id:
                    return True, student["student_id"]
    return False, None

# Log queries
def log_query(student_id, course_id, query_text, response_text):
    data = load_json(QUERIES_FILE)
    query_id = str(uuid.uuid4())
    data["queries"].append({
        "query_id": query_id,
        "student_id": student_id,
        "course_id": course_id,
        "query_text": query_text,
        "response_text": response_text,
        "asked_at": datetime.now().isoformat()
    })
    save_json(QUERIES_FILE, data)

# ML model call
def ask_backend(question: str, student_id: str, course_id: str):
    # Check registration using student_id
    data = load_json(STUDENTS_FILE)
    registered = False

    for student in data["students"]:
        if student["student_id"] == student_id:
            for course in student["courses"]:
                if course["course_id"] == course_id:
                    registered = True
                    break
            break

    if not registered:
        return f"🚫 Please register for {course_id}. You are not registered."
    try:
        url = "http://127.0.0.1:8000/answer"
        payload = {
            "question": question,
            "student_id": student_id,
            "course_id": course_id
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            return f"⚠️ Backend error ({response.status_code}): {response.text}"

        data = response.json()
        answer = data.get("answer", "🤖 Sorry, I couldn't find an answer.")
        sources = data.get("sources", [])
        return f"{answer}\n\n📚 **Sources:** {sources}"

    except Exception as e:
        return f"Error connecting to backend: {str(e)}"
    
# Discord setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} is online!")

@bot.event
async def on_member_join(member):
    general_channel = discord.utils.get(member.guild.text_channels, name='general')
    if general_channel:
        await general_channel.send(f"👋 Welcome {member.mention}! Please register to this course by sending the /register command")

# Ask command
@bot.tree.command(name="ask", description="Ask a question to the bot")
async def ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer(thinking=True)
    course_id = interaction.guild.name.replace(" ", "").upper()  # using server name as course_id
    registered, student_id = is_registered(interaction.user.id, course_id)

    if not registered:
        await interaction.response.send_message(
            f"🚫 You are not registered for {course_id}. Please register to this course by sending the /register command",
            ephemeral=True
        )
        return

    answer = ask_backend(question, student_id, course_id)
    log_query(student_id, course_id, question, answer)
    await interaction.followup.send(f"🤖 {answer}")

# Register to the course         ->>>>>>>>>>>>> could I clean this using a modal/form for the student?
@bot.tree.command(name="register", description="Register for the course")
async def register(interaction: discord.Interaction):
    course_id = interaction.guild.name.replace(" ", "").upper()
    data = load_json(STUDENTS_FILE)

    for student in data["students"]:
        if student["discord_id"] == str(interaction.user.id):
            for course in student["courses"]:
                if course["course_id"] == course_id:
                    await interaction.response.send_message(
                        f"✅ You are already registered for {course_id}.",
                        ephemeral=True
                    )
                    return
            student["courses"].append({
                "course_id": course_id,
                "registered_at": datetime.now().isoformat()
            })
            save_json(STUDENTS_FILE, data)
            await interaction.response.send_message(f"✅ Successfully registered for {course_id}!", ephemeral=True)
            return

    new_student = {
        "student_id": str(uuid.uuid4()),
        "discord_id": str(interaction.user.id),
        "name": interaction.user.name,
        "courses": [{
            "course_id": course_id,
            "registered_at": datetime.now().isoformat()
        }]
    }
    data["students"].append(new_student)
    save_json(STUDENTS_FILE, data)
    await interaction.response.send_message(f"✅ Successfully registered for {course_id}!", ephemeral=True)

# Help command
@bot.tree.command(name="help", description="Get help about the bot commands")
async def help_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        "📚 **CyBot Help Menu**\n\n"
        "Here are the available commands:\n"
        "• `/register` → Register yourself for this course so you can start asking questions.\n"
        "• `/ask [question]` → Ask a course-related question and get an ML-generated answer.\n"
        "• `/status` → Check which courses you are registered in (coming soon).\n"
        "• `/help` → Show this menu.\n\n"
        "⚠️ Note: You must be registered for the course before you can use `/ask`."
    )

bot.run(DISCORD_TOKEN)
