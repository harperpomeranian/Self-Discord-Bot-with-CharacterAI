# This code is licensed under CC BY 4.0

import discord
import json
import re

from characterai import aiocai
from dotenv import load_dotenv; load_dotenv()
from os import getenv
from asyncio import run, create_task, sleep
from os.path import exists as file_exists
from random import uniform

dc_client = discord.Client()
cai_client = None

# Character AI
character_id: str = getenv('CHARACTER_ID')
character_name: str = None
cai_chat = None
cai_me = None

# Other
is_generating_reply = False
server_or_channel_whitelist = []

# Be noteful when changing this
MESSAGE_SUFFIX = '\n-# This message was made with AI'

@dc_client.event
async def on_ready() -> None:
    print(f"Finished logging in as {dc_client.user}!")

@dc_client.event
async def on_message(message: discord.Message) -> None:
    global character_id, character_name, server_or_channel_whitelist
    
    # Whitelist
    whitelist_equiv = message.channel.id if not message.guild else message.guild.id
    if whitelist_equiv not in server_or_channel_whitelist and len(server_or_channel_whitelist) > 0:
        print(whitelist_equiv, 'is not in whitelist...')
        return
    
    if message.author == dc_client.user or not (isinstance(message.channel, (discord.channel.DMChannel)) or dc_client.user in message.mentions):
        # Custom commands
        if not message.content.startswith('-!'):
            return
        
        cmd_params: list[str] = message.content.split(' ')[1:]
        if len(cmd_params) == 0:
            return
        
        cmd: str = message.content[2:message.content.find(' ')].lower()
        from_me: bool = message.author == dc_client.user
        
        if cmd == 'botset':
            print('Loading new character...')
            await load_char(cmd_params[0])
            reply_message = await message.reply('Done! New CharacterAI Bot: ' + character_name)
        elif cmd == 'refresh' and from_me:
            load_configuration()

        # Delete the command messages
        await sleep(1)
        if message.channel.permissions_for(dc_client.user).manage_messages or from_me:
            await message.delete()
        if reply_message:
            await reply_message.delete()
        return
    
    # Put the history loading here so the AI won't get confused
    print(f'Loading History of {message.channel.name}')
    previous_messages: list[str] = []
    async for msg in message.channel.history():
        if msg.author != dc_client.user:
            previous_messages.append(f'{msg.author.name}: {await fix_message_content(msg.content)}')
        elif msg.content.endswith(MESSAGE_SUFFIX):
            previous_messages.append(f'{character_name}: {msg.content.replace(MESSAGE_SUFFIX, "")}')
    
    previous_messages.append('\nYou are now talking to: ' + message.author.name)
    previous_messages = reversed(previous_messages)
    
    # Prevent the AI from overloading
    if is_generating_reply:
        print(f'Waiting for my turn...')
        
    while is_generating_reply:
        await sleep(.1)
    
    print('Randomly waiting...')
    await sleep(uniform(2.0, 6.0))
    async with message.channel.typing():
        await message.reply(await reply_to_discord(message, previous_messages) + MESSAGE_SUFFIX)

async def fix_message_content(message: str) -> str:
    # Replace discord user ids with actual usernames
    for user_id in re.findall(r'<@(\d+)>', message):
        username: str = 'UnknownUser'
        try:
            user: discord.User = await dc_client.fetch_user(int(user_id))
            if user:
                username = user.name
        except Exception:
            pass
        
        message = message.replace(f'<@{user_id}>', username)
    
    # Replace discord channel ids with actual channel names
    for channel_id in re.findall(r'<#(\d+)>', message):
        channel_name: str = 'UnknownChannel'
        try:
            channel: discord.TextChannel = await dc_client.fetch_channel(int(channel_id))
            if channel:
                channel_name = channel.name
        except Exception:
            pass
        
        message = message.replace(f'<#{channel_id}>', channel_name)
    
    return message

async def reply_to_discord(message: discord.Message, message_history: list[str]) -> str:
    global is_generating_reply
    
    is_generating_reply = True
    print(f'Replying to `{message.content}`...')
    
    new_chat, _ = await cai_chat.new_chat(character_id, cai_me.id)
    # await sleep(.5)  # Prevent `comment` problem
    sent_message = await cai_chat.send_message(character_id, new_chat.chat_id, '\n'.join(message_history))
    
    is_generating_reply = False
    return sent_message.text

async def load_char(char_id: str) -> None:
    global character_id, character_name
    
    character_name = (await cai_client.get_char(char_id)).name
    character_id = char_id

def load_configuration() -> None:
    global server_or_channel_whitelist
    
    if file_exists('whitelist.json'):
        server_or_channel_whitelist = json.load(open('whitelist.json', 'r'))

async def main() -> None:
    global cai_client, cai_chat, cai_me, character_name
    
    load_configuration()
    
    # Login and setup CharacterAI
    cai_client = aiocai.Client(getenv('CHARACTER_AI_TOKEN'))
    cai_me = await cai_client.get_me()
    cai_chat = await cai_client.connect()
    
    await load_char(character_id)
    print('CharacterAI Bot:', character_name)
    
    # Start Self-Discord Bot
    await create_task(dc_client.start(getenv('DISCORD_TOKEN')))

if __name__ == '__main__':
    run(main())
