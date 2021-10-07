import functools
import discord
import aiohttp
from redbot.core import commands
from wand.image import Image
from io import BytesIO
import functools
import asyncio
import urllib

MAX_SIZE = 8 * 1000 * 1000


class ImageFindError(Exception):
    """Generic error for the _get_image function."""

    pass


class Buzz(commands.Cog):
    """Runs a Content Aware Scale filter on images."""

    def __init__(self, bot):
        self.bot = bot
        self.imagetypes = ["png", "jpg", "jpeg"]

    @staticmethod
    def _buzz(img):
        temp = BytesIO()
        temp.name = "buzzed.jpeg"
        frames = []
        with Image(file=img) as image:
            image.transform(resize="x256")
            # for i in range(85):
            #     with image.clone() as liquid:
            #         liquid.liquid_rescale()
            image.liquid_rescale(128, 128)
            image.save(temp)
        temp.seek(0)
        return temp

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
            path = urllib.parse.urlparse(link).path
            if not any(path.lower().endswith(x) for x in self.imagetypes):
                raise ImageFindError(
                    f"That does not look like an image of a supported filetype. Make sure you provide a direct link."
                )
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(link) as response:
                        resp = await response.read()
                        img = BytesIO(resp)
                except (OSError, aiohttp.ClientError):
                    raise ImageFindError(
                        "An image could not be found. Make sure you provide a direct link."
                    )
        else:  # image attached directly
            path = urllib.parse.urlparse(ctx.message.attachments[0].url).path
            if not any(path.lower().endswith(x) for x in self.imagetypes):
                raise ImageFindError(
                    f"That does not look like an image of a supported filetype. Make sure you provide a direct link."
                )
            if ctx.message.attachments[0].size > filesize_limit:
                raise ImageFindError("That image is too large.")
            temp_orig = BytesIO()
            await ctx.message.attachments[0].save(temp_orig)
            temp_orig.seek(0)
            img = temp_orig
        return img

    @commands.command()
    @commands.bot_has_permissions(attach_files=True)
    async def buzz(self, ctx, link: str = None):
        """
        "Buzzes" images into short GIFs using Content Aware Scaling.

        Use the optional parameter "link" to use a **direct link** as the target.
        """
        async with ctx.typing():
            try:
                img = await self._get_image(ctx, link)
            except ImageFindError as error:
                return await ctx.send(error)
            task = functools.partial(self._buzz, img)
            task = self.bot.loop.run_in_executor(None, task)
            try:
                image = await asyncio.wait_for(task, timeout=60)
            except asyncio.TimeoutError:
                return await ctx.send("The image took too long to process.")
            try:
                await ctx.send(file=discord.File(image))
            except discord.errors.HTTPException:
                return await ctx.send("That image is too large.")

    async def red_delete_data_for_user(self, **kwargs):
        """Nothing to delete."""
        return
