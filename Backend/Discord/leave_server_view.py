import discord
import logging
from .cybot_service import is_discord_admin

logger = logging.getLogger(__name__)

class LeaveServerView(discord.ui.View):
    def __init__(self, guilds):
        super().__init__(timeout=60)
        self.add_item(LeaveServerSelect(guilds))


class LeaveServerSelect(discord.ui.Select):
    def __init__(self, guilds):
        options = []

        for g in guilds[:25]:  # Discord limit = 25 options
            options.append(
                discord.SelectOption(
                    label=g.name,
                    value=str(g.id),
                    description=f"ID: {g.id}"
                )
            )

        super().__init__(
            placeholder="Choose a server...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        # Re-check admin
        is_admin = await is_discord_admin(str(interaction.user.id))
        if not is_admin:
            await interaction.response.send_message(
                "🚫 Not authorized.",
                ephemeral=True
            )
            return

        guild_id = int(self.values[0])
        guild = interaction.client.get_guild(guild_id)

        if not guild:
            await interaction.response.send_message(
                "❌ Server not found.",
                ephemeral=True
            )
            return

        name = guild.name

        await interaction.response.send_message(
            f"⚠️ Removing bot from **{name}**...",
            ephemeral=True
        )

        try:
            await guild.leave()
            # optional logging
            logger.info(f"Bot left guild: {name} ({guild_id})")
        except Exception as e:
            await interaction.followup.send(
                f"❌ Failed to leave server: {e}",
                ephemeral=True
            )