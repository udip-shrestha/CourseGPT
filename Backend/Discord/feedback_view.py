import discord
from .cybot_service import submit_vote

class FeedbackView(discord.ui.View):
    def __init__(self, course_id: str, student_id: str, query_id: str):
        super().__init__(timeout=300)
        self.course_id = course_id
        self.student_id = student_id
        self.query_id = query_id

    async def send_vote(self, interaction, vote: str):
        try:
            success, message = await submit_vote(
                self.course_id,
                self.student_id,
                self.query_id,
                vote,
            )
            if success:
                await interaction.response.send_message("✅ Feedback recorded. Thanks!", ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ {message}", ephemeral=True)
        except Exception:
            await interaction.response.send_message("❌ Error sending feedback.", ephemeral=True)

        # Disable buttons after voting
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(view=self)

    @discord.ui.button(label="👍 Helpful", style=discord.ButtonStyle.success)
    async def upvote(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.send_vote(interaction, "up")

    @discord.ui.button(label="👎 Not Helpful", style=discord.ButtonStyle.danger)
    async def downvote(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.send_vote(interaction, "down")