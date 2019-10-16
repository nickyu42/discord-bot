import discord 
from discord.ext import commands

import json
import os

from .saucenaopy.saucenao import SauceNAO


def get_api_key():
	"""
	Get api key from credentials file
	TODO: make a global credentials object
	"""
	with open(os.getcwd() + '/cogs/saucenaopy/saucenao.json', 'r') as f:
		return json.load(f)['API_KEY']


def parse_sauce_response(response):
	"""
	:param: requests.Response object to parse
	:return: parsed Dict
	"""
	results = response.json()['results']

	# sort based on similarity
	results.sort(key=lambda res: float(res['header']['similarity']))

	return results


def sauce_to_string(result):
	"""
	Converts a result into text that the bot can say
	TODO: Hacky code
	"""

	# leave only 1 url
	result['data']['url'] = result['data']['ext_urls'][0]
	result['data'].pop('ext_urls')

	# remove empty source
	if 'source' in result['data'] and result['data']['source']:
		result['data'].pop(source)

	content = ''.join(['{}: {}\n'.format(key, val) for key, val in result['data'].items()])

	ret = '- - -\nSimilarity: {}%\n{}- - -'.format(
		result['header']['similarity'], 
		content
	)

	return ret


class SourceRequester:
	def __init__(self, bot):
		self.bot = bot
		self.sn = SauceNAO(get_api_key())

	def get_source(self, url: str):
		response = self.sn.get_sauce(url)

		if response is None:
			return None

		results = parse_sauce_response(response)

		if len(results):
			return sauce_to_string(results[-1])
		else:
			return None

	@commands.group()
	async def sauce(self):
		#messages = self.bot.messages
		#await self.bot.say(self.bot.messages[-1].embeds)
		pass

	@sauce.command()
	async def url(self, *, url: str):
		"""
		response = self.sn.get_sauce(text)

		if response is None:
			await self.bot.say('No sauce found')
			return

		results = parse_sauce_response(response)

		if len(results):
			await self.bot.say(sauce_to_string(results[-1]))
		else:
			await self.bot.say('No sauce found')
		"""
		result = self.get_source(url)

		if result is not None:
			await self.bot.say(result)
		else:
			await self.bot.say('No sauce found')


def setup(bot):
    bot.add_cog(SourceRequester(bot))
