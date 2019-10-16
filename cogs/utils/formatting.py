"""
Utilities specific to discord.py api
"""

def convert_to_codeblock(string):
    """ 
    Method adds markdown syntax to keep the formatting intact 
    discord uses different formatting for messages
    so instead of a message we use a code block 

    :param string: self explanatory
    """
    return '```\n' + string + '```\n'