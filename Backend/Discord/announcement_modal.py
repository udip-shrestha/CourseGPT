import discord
import asyncio
from datetime import datetime

class AnnouncementModal(discord.ui.Modal, title="CourseGPT Announcement"):

    def __init__(self, is_admin_func):
        super().__init__()
        self.is_admin_func = is_admin_func

    version = discord.ui.TextInput(
        label="Version",
        placeholder="e.g. v1.1.0",
        required=True,
        max_length=20
    )

    message = discord.ui.TextInput(
        label="Announcement Message",
        style=discord.TextStyle.paragraph,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        version = self.version.value
        message = self.message.value

        await interaction.response.defer(thinking=True, ephemeral=True)

        embed = discord.Embed(
            title=f"📢 CourseGPT Update — {version}",
            description=f"{message}\n\n*This announcement was sent to all servers where CourseGPT is present.*",
            color=discord.Color.blue()
        )

        embed.set_footer(text="CourseGPT • AI-powered course assistant")
        embed.timestamp = datetime.now()

        success = 0
        failed = 0
        sent_channels = []

        # target_guild_name = "CPRE4910 - CourseGPT"

        for guild in interaction.client.guilds:
            # if guild.name != target_guild_name:      
            #     continue
            try:
                # Try to find #general first
                channel = discord.utils.get(guild.text_channels, name="general")

                # Fallback: first channel bot can send messages in
                if not channel:
                    for ch in guild.text_channels:
                        if ch.permissions_for(guild.me).send_messages:
                            channel = ch
                            break

                if channel:
                    await channel.send(embed=embed)
                    success += 1
                    sent_channels.append(f"{guild.name}: #{channel.name}")
                    await asyncio.sleep(1)
                else:
                    failed += 1

            except Exception:
                failed += 1

        followup_message = f"✅ Announcement sent!\nSuccess: {success}\nFailed: {failed}"
        if sent_channels:
            followup_message += "\n\nSent to channels:\n" + "\n".join(sent_channels)

        await interaction.followup.send(followup_message)