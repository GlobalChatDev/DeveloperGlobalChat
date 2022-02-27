from typing import Optional

import discord


class BasicButtons(discord.ui.View):
    def __init__(self, ctx, *, timeout: float = 180.0):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.value: Optional[bool] = None

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success, emoji="✅")
    async def accept(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(view=None)
        self.value = True
        self.stop()

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.danger, emoji="❌")
    async def denied(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(view=None)
        self.value = False
        self.stop()

    async def interaction_check(self, item: discord.ui.Item, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                content=f"You Can't Use that button, {self.ctx.author.mention} is the author of this message.",
                ephemeral=True,
            )

        return True
