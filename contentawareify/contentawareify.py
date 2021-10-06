import discord
import aiohttp
from redbot.core import commands
from redbot.core import Config
from redbot.core import checks
from wand.image import Image
from io import BytesIO
import functools
import asyncio
import urllib

MAX_SIZE = 8 * 1000 * 1000


class ImageFindError(Exception):
    """Generic error for the _get_image function."""

    pass


class ContentAwareify(commands.Cog):
    """Runs a Content Aware Scale filter on images."""

    def __init__(self, bot):
        self.bot = bot
        self.imagetypes = ["png", "jpg", "jpeg"]

    @staticmethod
    def _liquidrescale(img):
        with Image(img) as image:
            base = image.transform(resize="x256")

    async def _get_image(self, ctx, link):
        """Helper function to find an image."""
        if ctx.guild:
            filesize_limit = ctx.guild.filesize_limit
        else:
            filesize_limit = MAX_SIZE
        if not ctx.message.attachments and not link:
            async for msg in ctx.channel.history(limit=10):
                for attachment in msg.attachments:
                    path = urllib.parse.urlparse(attachment.url).path
                    if any(path.lower().endswith(x) for x in self.imagetypes):
                        link = attachment.url
                        break
                if link:
                    break
            if not link:
                raise ImageFindError("Please provide an attachment.")
        if link:
            path = urllib.parse.urlparse

    async def red_delete_data_for_user(self, **kwargs):
        """Nothing to delete."""
        return
