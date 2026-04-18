from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from typing import List, Dict, Any, Optional
from API.Service.discord_admins_service import DiscordAdminsService
from API.dependencies import get_discord_admins_service
from Metrics.metrics import MetricsRoute
from pydantic import BaseModel

router = APIRouter(prefix="/discord-admins", tags=["Discord Admins"], route_class=MetricsRoute)


class DiscordAdminRequest(BaseModel):
    discord_id: str
    name: str


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Discord admin",
    description="Adds a new Discord user as an admin."
)
def create_discord_admin(
    request: DiscordAdminRequest,
    service: DiscordAdminsService = Depends(get_discord_admins_service),
) -> Dict[str, str]:
    """Creates and persists a new Discord admin."""
    try:
        res = service.create_discord_admin(discord_id=request.discord_id, name=request.name)
        return {
            "admin_id": res.get("admin_id"),
            "message": "Discord admin created successfully."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create Discord admin: {str(e)}"
        )


@router.get(
    "/{discord_id}",
    status_code=status.HTTP_200_OK,
    summary="Get a Discord admin by ID",
    description="Retrieves a specific Discord admin by their Discord ID."
)
def get_discord_admin(
    discord_id: str = Path(..., description="The Discord ID of the admin"),
    service: DiscordAdminsService = Depends(get_discord_admins_service),
):
    """Returns the Discord admin details."""
    try:
        admin = service.get_discord_admin(discord_id=discord_id)
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Discord admin with ID {discord_id} not found."
            )
        return admin
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve Discord admin: {str(e)}"
        )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="List all Discord admins",
    description="Retrieve all Discord admins with optional pagination."
)
def get_all_discord_admins(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: DiscordAdminsService = Depends(get_discord_admins_service),
):
    """Returns a dictionary containing 'total' and 'admins' list."""
    try:
        return service.get_all_discord_admins(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve Discord admins: {str(e)}"
        )


@router.delete(
    "/{discord_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a Discord admin",
    description="Permanently deletes a Discord admin by their Discord ID."
)
def delete_discord_admin(
    discord_id: str = Path(..., description="The Discord ID of the admin to delete"),
    service: DiscordAdminsService = Depends(get_discord_admins_service),
):
    """Deletes the specified Discord admin."""
    try:
        service.delete_discord_admin(discord_id=discord_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete Discord admin: {str(e)}"
        )