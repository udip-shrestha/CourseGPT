import discord
import os
import time
from discord import app_commands
import httpx
import asyncio
from datetime import datetime
from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv
from .cybot_service import *
from Metrics.metrics import discord_command_count, discord_command_duration
from prometheus_client import start_http_server
from .announcement_modal import AnnouncementModal
from .feedback_view import FeedbackView
from .leave_server_view import LeaveServerView

import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)  # important for systemd
    ]
)

logger = logging.getLogger("cybot")

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    
# Discord setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    start_http_server(9091, addr="0.0.0.0")  # Start Prometheus metrics server on port 9091
    await bot.tree.sync()
    logger.info(f"{bot.user} is online!")
    # register existing members when bot starts
    for guild in bot.guilds:
        for member in guild.members:
            if not member.bot:
                await auto_register_member(member)

@bot.event
async def on_member_join(member):
    if not member.bot:
        await auto_register_member(member)
        await member.send(
            f"👋 Welcome {member.display_name}! You’ve been auto-registered for {member.guild.name}."
        )

@bot.event
async def on_guild_join(guild):
    logger.info(f"Bot added to guild: {guild.name}")
    for member in guild.members:
        if not member.bot:
            await auto_register_member(member)

# Ask command
@bot.tree.command(name="ask", description="Ask a question to the bot")
@app_commands.describe(question="Your question about the course material of this course", image="Optionally attach an image with your question to get more specific answers (e.g. a graph, diagram, or handwritten notes)")
async def ask(interaction: discord.Interaction, question: str, image: Optional[discord.Attachment] = None):
    command_name = "ask"
    start = time.time()
    outcome = "success"
    try:
        # Get course_id from guild name using API
        guild_name = interaction.guild.name if interaction.guild else ""
        course_id = await get_course_id(guild_name)
        
        if not course_id:
            await interaction.response.send_message(
                "🚫 Course not found. Please ask an instructor to create the course first.",
                ephemeral=True
            )
            return

        # Check if student is registered
        registered, student_id = await is_registered_discord(str(interaction.user.id), course_id)
        if not registered:
            await interaction.response.send_message(
                f"🚫 You are not registered for this course. Please try registering using the /register command first.",
                ephemeral=True
            )
            return

        # Prepare image data
        image_bytes = None
        image_name = None
        image_mime = None

        if image:
            # Validate file type
            if not image.filename.lower().endswith((".png", ".jpg", ".jpeg")):
                await interaction.response.send_message(
                    "❌ Invalid file type. Please upload PNG, JPG, or JPEG.",
                    ephemeral=True
                )
                return
            
            # Defer response while we process the image
            await interaction.response.defer(thinking=True)

            # Download image
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(image.url)
                if resp.status_code == 200:
                    image_bytes = resp.content
                    image_name = image.filename
                    image_mime = resp.headers.get("content-type")
                else:
                    await interaction.followup.send(
                        "❌ Failed to download the image.",
                        ephemeral=True
                    )
                    return
        else:
            await interaction.response.defer(thinking=True)
            
        # Get answer from AI model (with optional image)
        answer, sources, query_id = await ask_AI_model(question, course_id, image_bytes, image_name, image_mime)

        # Format response with sources if available
        response = answer

        # Safely verify sources is a non-empty list of strings
        if isinstance(sources, list):
            clean_sources = [s for s in sources if isinstance(s, str) and s.strip()]
            if clean_sources:
                formattedSources = await formatSources(clean_sources)
                if formattedSources:
                    response += "\n\n📚 **Sources:**\n" + formattedSources

        # Send response in chunks if it exceeds Discord's 2000 character limit
        message_chunks = await split_message(response)
        for i, chunk in enumerate(message_chunks):
            if not chunk.strip():
                continue

            if i == len(message_chunks) - 1 and query_id:
                await interaction.followup.send(
                    chunk,
                    view=FeedbackView(course_id, student_id, query_id)
                )
            else:
                await interaction.followup.send(chunk)
    except Exception as e:
        outcome = "error"
        logger.exception("Error in /ask command: {e}")
        raise
    finally:
        duration = time.time() - start
        try:
            discord_command_count.labels(command=command_name, outcome=outcome).inc()
            discord_command_duration.labels(command=command_name, outcome=outcome).observe(duration)
        except Exception:
            pass

# Register to the course        
@bot.tree.command(name="register", description="Register for the course")
async def register(interaction: discord.Interaction):
    command_name = "register"
    start = time.time()
    outcome = "success"
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        # Get course_id from guild name using API
        guild_name = interaction.guild.name if interaction.guild else ""
        course_id = await get_course_id(guild_name)
        
        if not course_id:
            await interaction.followup.send(
                "🚫 Course not found. Please ask an instructor to create the course first."
            )
            return
        
        # Check if student is already registered
        registered, _ = await is_registered_discord(str(interaction.user.id), course_id)
        if registered:
            await interaction.followup.send(
                "🚫 You are already registered for this course."
            )
            return
        
        # Register student using API
        success, message, student_id = await register_student(
            str(interaction.user.id),
            interaction.user.name,
            course_id
        )

        # Send response based on registration result
        emoji = "✅" if success else "🚫"
        await interaction.followup.send(f"{emoji} {message}")
    except Exception:
        outcome = "error"
        raise
    finally:
        duration = time.time() - start
        try:
            discord_command_count.labels(command=command_name, outcome=outcome).inc()
            discord_command_duration.labels(command=command_name, outcome=outcome).observe(duration)
        except Exception:
            pass

# Check registration status
@bot.tree.command(name="status", description="Check if you are registered for this course")
async def status(interaction: discord.Interaction):
    command_name = "status"
    start = time.time()
    outcome = "success"
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        # Get course_id from guild name
        guild_name = interaction.guild.name if interaction.guild else ""
        course_id = await get_course_id(guild_name)
        
        if not course_id:
            await interaction.followup.send(
                "🚫 Course not found. Please ask an instructor to create the course first."
            )
            return
        
        # Check if student is registered
        registered, _ = await is_registered_discord(str(interaction.user.id), course_id)
        if registered:
            await interaction.followup.send("✅ You are registered for this course.")
        else:
            await interaction.followup.send("🚫 You are not registered for this course.")
            return
    except Exception:
        outcome = "error"
        raise
    finally:
        duration = time.time() - start
        try:
            discord_command_count.labels(command=command_name, outcome=outcome).inc()
            discord_command_duration.labels(command=command_name, outcome=outcome).observe(duration)
        except Exception:
            pass

# Check registered courses
@bot.tree.command(name="courses", description="Check which courses you are registered in")
async def courses(interaction: discord.Interaction):
    command_name = "courses"
    start = time.time()
    outcome = "success"
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        discord_id = str(interaction.user.id)
        courses = await get_student_courses(discord_id)

        if not courses:
            await interaction.followup.send("🚫 You are not registered in any courses yet.", ephemeral=True)
            return

        # Build a formatted message for all courses
        message = "📘 **Courses you are registered in:**\n"
        for c in courses:
            course_name = c.get("course_name", "Unknown")
            year = c.get("year", "")
            institution = c.get("institution", "")
            message += f"- **{course_name}** ({institution}, {year})\n"

        await interaction.followup.send(message, ephemeral=True)
    except Exception:
        outcome = "error"
        raise
    finally:
        duration = time.time() - start
        try:
            discord_command_count.labels(command=command_name, outcome=outcome).inc()
            discord_command_duration.labels(command=command_name, outcome=outcome).observe(duration)
        except Exception:
            pass


# Feedback command
@bot.tree.command(name="feedback", description="Feel free to submit any feedback about CourseGPT or our bot design")
@app_commands.describe(feedback="Your feedback about CourseGPT or the Discord bot")
async def feedback(interaction: discord.Interaction, feedback: str):
    command_name = "feedback"
    start = time.time()
    outcome = "success"
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        guild_name = interaction.guild.name if interaction.guild else ""
        course_id = await get_course_id(guild_name)

        if not course_id:
            await interaction.followup.send(
                "🚫 Course not found. Please ask an instructor to create the course first.",
                ephemeral=True
            )
            return

        # Ensure the user is registered before accepting feedback
        registered, _ = await is_registered_discord(str(interaction.user.id), course_id)
        if not registered:
            await interaction.followup.send(
                "🚫 You must be registered for this course to submit feedback.",
                ephemeral=True
            )
            return

        # Submit feedback to backend
        success, message, feedback_id = await submit_feedback(course_id, feedback)
        emoji = "✅" if success else "🚫"
        await interaction.followup.send(f"{emoji} {message}")
    except Exception:
        outcome = "error"
        raise
    finally:
        duration = time.time() - start
        try:
            discord_command_count.labels(command=command_name, outcome=outcome).inc()
            discord_command_duration.labels(command=command_name, outcome=outcome).observe(duration)
        except Exception:
            pass

# Unregister from a course        
@bot.tree.command(name="unregister", description="Unregister from a course given the course name")
@app_commands.describe(course_name="Name of the course to unregister from. Note: This is the Discord server name of that course.")
async def unregister(interaction: discord.Interaction, course_name: str):
    command_name = "unregister"
    start = time.time()
    outcome = "success"
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
        course_id = await get_course_id(course_name)
        
        if not course_id:
            await interaction.followup.send(
                "🚫 Course not found. Try a different course name or checking the spelling in /courses"
            )
            return
        
        # Check if student is already not registered
        registered, _ = await is_registered_discord(str(interaction.user.id), course_id)
        if not registered:
            await interaction.followup.send(
                "🚫 You are currently not registered for this course."
            )
            return
        
        # Unregister student using API
        success, message = await unregister_student(
            str(interaction.user.id),
            course_id
        )

        # Send response based on registration result
        if success:
            emoji = "✅"  
            disclaimer = "⚠️ Ensure to leave the course's Discord server to avoid being registered automatically." 
        else:
            emoji = "🚫"
            disclaimer = ""
        await interaction.followup.send(f"{emoji} {message}\n\n{disclaimer}")
    except Exception:
        outcome = "error"
        raise
    finally:
        duration = time.time() - start
        try:
            discord_command_count.labels(command=command_name, outcome=outcome).inc()
            discord_command_duration.labels(command=command_name, outcome=outcome).observe(duration)
        except Exception:
            pass

# Announce command (admin only)
@bot.tree.command(name="announce", description="Broadcast an announcement to all servers (admin only)")
async def announce(interaction: discord.Interaction):
    is_admin = await is_discord_admin(str(interaction.user.id))

    if not is_admin:
        await interaction.response.send_message(
            "🚫 You are not authorized to use this command. This will be reported to the Admin team",
            ephemeral=True
        )
        logger.warning(f"Unauthorized announce attempt by user ID {interaction.user.id}")
        return

    await interaction.response.send_modal(AnnouncementModal(is_discord_admin))

@bot.tree.command(name="leave_server", description="Remove bot from a server (admin only)")
async def leave_server(interaction: discord.Interaction):
    is_admin = await is_discord_admin(str(interaction.user.id))

    if not is_admin:
        await interaction.response.send_message(
            "🚫 You are not authorized to use this command. This will be reported to the Admin team",
            ephemeral=True
        )
        logger.warning(f"Unauthorized leave_server attempt by user ID {interaction.user.id}")
        return

    guilds = interaction.client.guilds

    if not guilds:
        await interaction.response.send_message(
            "Bot is not in any servers.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        "Select a server to remove the bot from:",
        view=LeaveServerView(guilds),
        ephemeral=True
    )

# Help command
@bot.tree.command(name="help", description="Get help about the bot commands")
async def help_command(interaction: discord.Interaction):
    command_name = "help"
    start = time.time()
    outcome = "success"
    try:
        await interaction.response.send_message(
            "📚 **CyBot Help Menu**\n\n"
            "Here are the available commands:\n"
            "• `/register` → (Optional) Manually register yourself for this course if not auto-registered.\n"
            "• `/ask [question] [Attach image]` → Ask a course-related question and optionally include an image to get an AI-generated answer.\n"
            "• `/status` → Check your registration status for this course.\n"
            "• `/courses` → Check which courses you are registered in.\n"
            "• `/feedback` → Share with us any feedback you have about CourseGPT.\n"
            "• `/unregister [course name]` → Unregister from a course given the course name (Discord server name).\n"
            "• `/help` → Show this menu.\n\n"
            "⚠️ Note: You must be registered for the course before you can use `/ask`."
        )
    except Exception:
        outcome = "error"
        raise
    finally:
        duration = time.time() - start
        try:
            discord_command_count.labels(command=command_name, outcome=outcome).inc()
            discord_command_duration.labels(command=command_name, outcome=outcome).observe(duration)
        except Exception:
            pass

bot.run(DISCORD_TOKEN)