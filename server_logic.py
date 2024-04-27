from mctools import RCONClient, errors
import asyncio
import os

# password for rcon communication
# IMPORTANT NOTE: MAKE SURE YOUR PASSWORD CONTAINS NO CHARACTERS WHICH WILL UPSET PYTHON (slashes, quotes)
password: str
host: str = "127.0.0.1"
rcon_port: str

# makes the user input all lowercase, returns true if input was intended as a command
def form(input: str) -> str:
    lowered_input = input.lower()

    if lowered_input[0] == "/":
        return lowered_input[1:], True
    return lowered_input, False
    
# define function to measure the size, in bytes, of a message passed to the bot.
# This is useful to prevent messages which are too long. Max accepted is 1441 bytes.
# NOT CURRENTLY IMPLEMENTED
def byte_size(string):
    return len(string.encode('utf-8'))
    
def mc_server_rcon(command: str) -> str:

    # create the client object
    rcon = RCONClient(host, rcon_port)
    print(command)
    if rcon.login(password):
        try:
            command_response = rcon.command(command)
            if command_response.encode('utf-8') != b'\x1b[0m':
                return command_response
            return "Command executed successfully."
        except errors.RCONLengthError:
            return "Command too long!!"
    else:
        return "Bad Password."


def discord_chat_forward(message: str):
    rcon = RCONClient(host, rcon_port)
    if rcon.login(password):
        rcon.command(f'say {message}')


# take the latest log file, compare it with the last saved one
# store all lines in lists, and subract leaving only the new entries behind
# then return that list.
# this also returns a bool saying whether or not any of the new entries were from chat
def read_new(file: str):
    new_log = open(file, "r")
    old_log = open("last_logged.txt", "r")

    latest: str = new_log.read()
    last_logged: str = old_log.read()
    temp: str = latest

    new_log.close()
    old_log.close()

    total: list = latest.splitlines()
    subtract: list = last_logged.splitlines()
    entries: list = []
    out_list: list = []

    total_len: int = len(total)
    subtract_len: int = len(subtract)

    for a in range(1, total_len - subtract_len + 1):
        entries.append(total[total_len - a])
    
    for x in range(len(entries)):
        filter: str = entries[x]

        # the specific syntax in the string in the if statement only occurs if the entry is from game chat
        # append all game chat entries to the output list after formatting them to look prettier
        if "[Server thread/INFO]: <" in filter:
            filter = filter[34:].replace(">", ": ", 1)
            out_list.append(filter)

    # update the last_logged file with the most recent entries
    update_log = open("last_logged.txt", "w")
    update_log.write(temp)

    #only return true if there are chat entries
    if len(out_list) == 0:
        return False, []
    
    out_list.reverse()
    return True, out_list


# get time mc server log was last modified from os, fetch every second and wait from it to change
# upon change, get the new entries and return them as a list
async def get_change(file_path, interval=1) -> list:
    last_modified = os.path.getmtime(file_path)
    while True:
        current_modified = os.path.getmtime(file_path)
        if current_modified != last_modified:
            is_chat = read_new(file_path)
            last_modified = current_modified
            if is_chat[0]:
                return is_chat[1] 
            return is_chat[1]
        await asyncio.sleep(interval)
