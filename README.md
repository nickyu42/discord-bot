# Discord bot for the Wine-Connoisseurs guild

## Overview 

### Dependencies
- python >= 3.7
- discord.py == 1.2.3
- requests == 2.22.0

### Docker setup
The bot can be run in a docker container

To build the image  
```docker build .```

To run the container as a daemon  
```docker run --restart always --name discord-bot -d -v ./cogs:/app/cogs discord```  
*The cogs volume needs to be mounted in /app/cogs
