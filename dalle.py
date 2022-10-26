import asyncio
import base64
import io

import logging


from discord.ext import commands,tasks
# from discord_slash import cog_ext,SlashCommand, SlashContext
# from discord_slash.utils.manage_commands import create_choice, create_option
from PIL import Image
import aiohttp

import numpy

import interactions

from interactions.api.models import flags as FLAGS
from interactions.api.models import channel as ChannelAPI
from interactions.api.models import presence
from interactions.api.models import member
from interactions.ext.files import command_send

backend_url = "https://bf.dallemini.ai/generate"
format = "PNG"
IMAGE_SELECT_TIMEOUT = 10800
'''
class ImageSelect(discord.ui.Select):
    def __init__(self, collage: discord.File, images: list[discord.File]):
        options = [discord.SelectOption(label='Image collage')] + [discord.SelectOption(label=f'Image {i + 1}') for i in range(len(images))]
        super().__init__(placeholder='Select an image',
                         min_values=1, max_values=1, options=options)
        self.collage = collage
        self.images = images

    async def callback(self, ctx):
        await ctx.defer()
        if self.values[0] == 'Image collage': 
            self.collage.fp.seek(0)
            #await ctx.message.edit(attachments=[self.collage])
        else:
            image_index = int(self.values[0].split(' ')[-1]) - 1
            self.images[image_index].fp.seek(0)
            #await interaction.edit_original_message(attachments=[self.images[image_index]])



class ImageSelectView(discord.ui.View):
    def __init__(self, collage: discord.File, images: list[discord.File], timeout: float):
        super().__init__(timeout=timeout)
        self.add_item(ImageSelect(collage, images))
''' 



       
async def generate_images(prompt: str) -> list[io.BytesIO]:
    async with aiohttp.ClientSession() as session:
        async with session.post(backend_url, json={'prompt': prompt}) as response:
            if response.status == 200:
                response_data = await response.json()
                images = [io.BytesIO(base64.decodebytes(bytes(image, 'utf-8')))
                          for image in response_data['images']]
                return images
            else:
                return None        
def make_collage_sync(images: list[io.BytesIO], wrap: int) -> io.BytesIO:
    image_arrays = [numpy.array(Image.open(image)) for image in images]
    for image in images:
        image.seek(0)
    collage_horizontal_arrays = [numpy.hstack(
        image_arrays[i:i + wrap]) for i in range(0, len(image_arrays), wrap)]
    collage_array = numpy.vstack(collage_horizontal_arrays)
    collage_image = Image.fromarray(collage_array)
    collage = io.BytesIO()
    collage_image.save(collage, format=format)
    collage.seek(0)
    return collage


async def make_collage(images: list[io.BytesIO], wrap: int) -> io.BytesIO:
    images = await asyncio.get_running_loop().run_in_executor(None, make_collage_sync, images, wrap)
    return images

        
class DALLE(interactions.Extension):
    def __init__(self,bot):
        self.bot = bot
        
    @interactions.extension_listener()
    async def on_ready(self):
        print("DALLE Mini On ready")
    
    @interactions.extension_command(
        name="generate",
        description="讓AI生成一張圖片",
        options=[
            interactions.Option(
                name = "prompt",
                description="描述",
                required = True,
                type = 3,
            
            )
        ]
    )
    async def _generate(self,ctx,prompt):
        await ctx.defer()
        images = None
        attempt = 0
        while not images:
            if attempt > 0:
                logging.warning(f'Image generate request failed on attempt {attempt} for prompt "{prompt}" issued by {interactions.user} (ID: {interactions.user.id})')
            attempt += 1
            images = await generate_images(prompt)

        print(f'Successfully generated images with prompt "{prompt}" from {ctx.author} (ID: {ctx.author.id}) on attempt {attempt}')
        collage = await make_collage(images, 3)
        collage = interactions.File(filename=f'collage.{format}',fp=collage)
        #collage = discord.File(collage, filename=f'collage.{format}')
        #images = [discord.File(images[i], filename=f'{i}.jpg') for i in range(len(images))]
        #await ctx.send(attachments=[collage])#view=ImageSelectView(collage, images, timeout=IMAGE_SELECT_TIMEOUT))
        await command_send(ctx,files=[collage])
        
    
def setup(bot):
    bot.load('interactions.ext.files')
    DALLE(bot)
        