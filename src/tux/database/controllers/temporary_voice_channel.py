"""
Temporary Voice Channel status controller.

This Controller manages the TempVC and who is the current owner
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from tux.database.controllers.base import BaseController
from tux.database.models import TemporaryVoiceChannel

if TYPE_CHECKING:
    from tux.database.service import DatabaseService


class TemporaryVoiceChannelController(BaseController[TemporaryVoiceChannel]):
    """Clean VC controller using the new BaseController pattern."""

    def __init__(self, db: DatabaseService | None = None) -> None:
        """Initialize the TempVC controller.

        Parameters
        ----------
        db : DatabaseService | None, optional
            The database service instance. If None, uses the default service.
        """
        super().__init__(TemporaryVoiceChannel, db)

    async def get_or_create_temporary_voice_channel(
        self,
        guild_id: int,
        voice_channel_id: int,
        owner_id: int,
    ) -> TemporaryVoiceChannel:
        """
        Get a VC, or create it with the given Inputs.

        Returns
        -------
        TemporaryVoiceChannel
            The VC (existing or newly created).
        """
        temporary_voice_channel = await self.get_temporary_voice_channel_by_id(
            guild_id,
            voice_channel_id,
        )
        if temporary_voice_channel is not None:
            return temporary_voice_channel
        return await self.create(
            guild_id=guild_id,
            voice_channel_id=voice_channel_id,
            owner_id=owner_id,
        )

    async def get_temporary_voice_channel_by_id(
        self,
        guild_id: int,
        channel_id: int,
    ) -> TemporaryVoiceChannel | None:
        """
        Get a Temp VC with the guild and channel id.

        Returns
        -------
        TemporaryVoiceChannel | None
            The VC if found, None otherwise.
        """
        return await self.find_one(
            filters=(TemporaryVoiceChannel.guild_id == guild_id)
            & (TemporaryVoiceChannel.voice_channel_id == channel_id),
        )

    async def get_temporary_voice_channel_by_owner_id(
        self,
        user_id: int,
    ) -> TemporaryVoiceChannel | None:
        """
        Get a Temp VC with the owner ID.

        Returns
        -------
        TemporaryVoiceChannel | None
            The VC if found, None otherwise.
        """
        return await self.find_one(filters=(TemporaryVoiceChannel.owner_id == user_id))

    async def delete_temporary_voice_channel(
        self,
        guild_id: int,
        channel_id: int,
    ) -> bool:
        """
        Delete a VC with the given Inputs.

        Returns
        -------
        bool
            True if deleted successfully, False otherwise.
        """
        voice_channel = await self.get_temporary_voice_channel_by_id(
            guild_id,
            channel_id,
        )
        if voice_channel is None:
            return False

        return await self.delete_by_id((guild_id, channel_id))

    async def handle_owner_left_time(
        self,
        guild_id: int,
        channel_id: int,
        owner_left: bool,
    ) -> TemporaryVoiceChannel | None:
        """
        Set the owner's left time.

        TODO: make the time configurable

        Returns
        -------
        TemporaryVoiceChannel
            The Changed Voice Channel.
        """
        if owner_left:
            return await self.update_by_id(
                (guild_id, channel_id),
                owner_left_time=(datetime.now(UTC) + timedelta(minutes=5)),
            )

        return await self.update_by_id(
            (guild_id, channel_id),
            owner_left_time=None,
        )
