from typing import Optional

from API.Repository.i_sql_repository import ISQLRepository
from API.Util.decorators import clean_service


class DiscordAdminsService:
    """
    Handles creation, retrieval, listing, and deletion of Discord admins.
    Interacts with the SQL repository to manage persistent Discord admin data.
    """

    def __init__(self, sql_repo: ISQLRepository):
        self.sql_repo = sql_repo

    # ------------------------------------------------------
    # Create Discord Admin
    # ------------------------------------------------------
    @clean_service
    def create_discord_admin(self, discord_id: str, name: str) -> dict:
        """
        Persist a Discord admin record.
        Returns a dict containing the new admin id.
        """
        admin_id = self.sql_repo.create_discord_admin(discord_id=discord_id, name=name)
        return {"admin_id": admin_id}

    # ------------------------------------------------------
    # Read Discord Admin
    # ------------------------------------------------------
    @clean_service
    def get_discord_admin(self, discord_id: str) -> Optional[dict]:
        """
        Retrieve a specific Discord admin by discord_id.
        """
        return self.sql_repo.read_discord_admin(discord_id=discord_id)

    # ------------------------------------------------------
    # List All Discord Admins
    # ------------------------------------------------------
    @clean_service
    def get_all_discord_admins(self, limit: int = 50, offset: int = 0) -> dict:
        """Retrieve all Discord admins with pagination."""
        return self.sql_repo.read_all_discord_admins(limit=limit, offset=offset)

    # ------------------------------------------------------
    # Delete Discord Admin
    # ------------------------------------------------------
    @clean_service
    def delete_discord_admin(self, discord_id: str) -> dict:
        """
        Permanently deletes a Discord admin record.
        """
        self.sql_repo.delete_discord_admin(discord_id=discord_id)
        return {"status": "deleted", "discord_id": discord_id}