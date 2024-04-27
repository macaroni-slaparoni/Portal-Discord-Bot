Portal Bot uses the RCON (remote console) protocol via the mctools library to talk to a Minecraft server,
and the discord.py library to drive a Discord bot.

DEPENDENCIES:
dotenv
discord
mctools

SETUP:
The Minecraft server and Portal Bot must be running on the same machine, for now
You must copy the token of your Discord bot into an environmental variable named "DISCORD_TOKEN"
Declare all the undeclared variables up to line 23 in main.py, and up to line 10 in server_logic.py

Tested to work on Python 3.8 and later
