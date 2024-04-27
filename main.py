from typing import Final
from os import getenv
from datetime import datetime
from dotenv import load_dotenv
from discord import Intents, Client, Message
from server_logic import form, mc_server_rcon, discord_chat_forward, get_change


# load token from an environmental variable named "DISCORD_TOKEN"
# I prefer to declare this using a .env file in this directory
load_dotenv()
TOKEN: Final[str] = getenv('DISCORD_TOKEN')

# replace with the id of the public channel you want to forward to the mc server
chat_forwarding_channel_id: int = 0

# ditto, but for commands
commands_channel_id: int = 0

# path to mc server log file
# MUST BE ON THE SAME MACHINE (as for needing so be on the same drive, I assume not but have yet to test)
log_path: str = ""

# bot setup
intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)


# function to log a message, with date and time
def log(text: str):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    log_file = open("bot_log.txt", "a")
    log_file.write(dt_string + "\n" + text + "\n\n")
    log_file.close()


# functionality
async def botMessage(message: Message, user_message: str, username: str) -> None:
    if not user_message:
        log('Message was empty, probably improper enabling of intents')

    id = message.channel.id

    try:
        formatted = form(user_message)
        lowered = formatted[0]
        command_bool: bool = formatted[1]

        # if the message was intended to be a command, send it to the server as a command
        if command_bool and id == commands_channel_id:
            response = mc_server_rcon(lowered)
            await message.channel.send(response)

        elif command_bool == False and id == commands_channel_id:
            await message.channel.send('Commands must start with a "/".')

        # forward all messages from a single channel to the mc server
        elif command_bool == False and id == chat_forwarding_channel_id:
            discord_chat_forward(username + ": " + user_message)

        elif command_bool and id == chat_forwarding_channel_id:
            await message.channel.send('You do not have permission to use commands.')

    except Exception as e:
        log("BOT FAILED TO MAKE OR SEND RESPONSE, ERROR: " + str(e))

# get mc server message from log file, then send it to discord server
async def send_chat_message():
    while True:
        messages: list = await get_change(log_path, 1)
        channel = client.get_channel(chat_forwarding_channel_id)

        for x in range(0, len(messages)):
            log(messages[x])
            await channel.send(messages[x])


# startup
@client.event
async def on_ready() -> None:
    log(f"{client.user} is now online")
    print(f"{client.user} is now online")
    await send_chat_message()


#incoming message handler
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    if message.channel.id == chat_forwarding_channel_id or commands_channel_id:
        log(f'user {username} sent {user_message} in channel {channel}')

    await botMessage(message, user_message, username)


# main entry point
def main() -> None:
    clear = open("last_logged.txt", "w")
    clear.write("")
    clear.close()
    
    client.run(token=TOKEN)

if __name__ == '__main__':
    main()
