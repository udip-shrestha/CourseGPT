import discord
import os
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import uuid
from dotenv import load_dotenv
from cybot_service import *

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    
# Discord setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} is online!")
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
    print(f"Bot added to guild: {guild.name}")
    for member in guild.members:
        if not member.bot:
            await auto_register_member(member)

# Ask command
@bot.tree.command(name="ask", description="Ask a question to the bot")
async def ask(interaction: discord.Interaction, question: str):
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
    registered, student_id = await is_registered(str(interaction.user.id), course_id)
    if not registered:
        await interaction.response.send_message(
            f"🚫 You are not registered for this course. Please try registering using the /register command first.",
            ephemeral=True
        )
        return
    
    # Defer response while we wait for AI
    await interaction.response.defer(thinking=True)

    # Get answer from AI model
    answer, sources = await ask_AI_model(question, course_id)
    
    # Log the query
    await log_query(student_id, course_id, question, answer)
    
    # Format response with sources if available
    response = answer
    if sources:
        values = sources.split("; ") 
        response += "\n\n📚 **Sources:**\n"
        for value in values:
            response += f"• {value}\n"

    # Send response in chunks if it exceeds Discord's 2000 character limit 
    message_chunks = await split_message(response)
    
    for i, chunk in enumerate(message_chunks):
        if chunk.strip():  # Only send non-empty chunks
            await interaction.followup.send(chunk)

# Register to the course        
@bot.tree.command(name="register", description="Register for the course")
async def register(interaction: discord.Interaction):
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
    registered, _ = await is_registered(str(interaction.user.id), course_id)
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

# Check registration status
@bot.tree.command(name="status", description="Check if you are registered for this course")
async def status(interaction: discord.Interaction):
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
    registered, _ = await is_registered(str(interaction.user.id), course_id)
    if registered:
        await interaction.followup.send(
            "✅ You are registered for this course."
        )
    else: 
        await interaction.followup.send(
            "🚫 You are not registered for this course."
        )
        return

# Check registered courses
@bot.tree.command(name="courses", description="Check which courses you are registered in")
async def courses(interaction: discord.Interaction):
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

# Unregister from the course        
@bot.tree.command(name="unregister", description="Unregister from the course")
async def unregister(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True, ephemeral=True)
    # Get course_id from guild name using API
    guild_name = interaction.guild.name if interaction.guild else ""
    course_id = await get_course_id(guild_name)
    
    if not course_id:
        await interaction.followup.send(
            "🚫 Course not found. Please ask an instructor to create the course first."
        )
        return
    
    # Check if student is already unregistered
    registered, _ = await is_registered(str(interaction.user.id), course_id)
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
        disclaimer = "⚠️ Ensure to leave the Discord server to avoid being registered automatically." 
    else:
        emoji = "🚫"
        disclaimer = ""
    await interaction.followup.send(f"{emoji} {message}\n\n{disclaimer}")


# Help command
@bot.tree.command(name="help", description="Get help about the bot commands")
async def help_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        "📚 **CyBot Help Menu**\n\n"
        "Here are the available commands:\n"
        "• `/register` → (Optional) Manually register yourself for this course if not auto-registered.\n"
        "• `/ask [question]` → Ask a course-related question and get an AI-generated answer.\n"
        "• `/status` → Check your registration status for this course (coming soon).\n"
        "• `/courses` → Check which courses you are registered in.\n"
        "• `/help` → Show this menu.\n\n"
        "⚠️ Note: You must be registered for the course before you can use `/ask`."
    )

bot.run(DISCORD_TOKEN)
