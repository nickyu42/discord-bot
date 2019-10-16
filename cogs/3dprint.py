from discord.ext import commands
from picamera import PiCamera
from time import sleep
from .utils import check


class Printer:
	"""Cog for manipulating the raspberry pi camera"""
	
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="capture", hidden=True)		
	@check.is_owner()
	async def _capture(self):
		# stream = BytesIO()
		
		with PiCamera() as camera:
			# wait 2s for the camera
			camera.start_preview()
			sleep(2)
			
			# TODO: fix hack
			camera.capture('./cogs/picam/test.jpg')	
			# camera.capture(stream, 'jpeg')
		
		with open('./cogs/picam/test.jpg', 'rb') as f:
			await self.bot.upload(f)

def setup(bot):
	bot.add_cog(Printer(bot))
	
