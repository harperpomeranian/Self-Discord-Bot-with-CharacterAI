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
discord2cai: dict[str, dict[str, str]] = {}

is_message_processing = False

# Be noteful when changing this
MESSAGE_SUFFIX = '\n-# This message was made with AI'

@dc_client.event
async def on_ready() -> None:
    print(f"Finished logging in as {dc_client.user}!")

@dc_client.event
async def on_message(message: discord.Message) -> None:
    global is_message_processing, character_id, character_name
    if message.author == dc_client.user or not (isinstance(message.channel, (discord.channel.DMChannel)) or dc_client.user in message.mentions):
        # Custom commands
        from_me = message.author == dc_client.user
        if message.content.startswith('!botset ') and from_me:
            print('Loading new character...')
            await load_char(message.content.replace('!botset ', ''))
            reply_message = await message.reply('Done! New CharacterAI Bot: ' + character_name)
            await sleep(1)
            await message.delete()
            await reply_message.delete()
        return
    
    print(f'Loading message history of {message.channel}...')
    previous_messages: list[str] = []
    async for msg in message.channel.history(limit=20):
        if msg.author != dc_client.user:
            previous_messages.append(f'{msg.author.name}: {await fix_message_content(msg.content)}')
        elif msg.content.endswith(MESSAGE_SUFFIX):
            previous_messages.append(f'{character_name}: {msg.content.replace(MESSAGE_SUFFIX, "")}')
        
    previous_messages = reversed(previous_messages)
    
    # Prevent the AI from overloading
    while is_message_processing:
        await sleep(.1)
    
    is_message_processing = True
    await sleep(uniform(2.0, 6.0))
    async with message.channel.typing():
        await message.reply(await reply_to_discord(message, previous_messages) + MESSAGE_SUFFIX)
    is_message_processing = False

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
    
    # Replace discord channel ids with channel usernames
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
    if str(message.channel.id) not in discord2cai:
        print(f'Channel {message.channel} isn\'t in memory, adding...')
        new_chat, _ = await cai_chat.new_chat(character_id, cai_me.id)
        await sleep(1.0)  # Prevent `comment` problem
        sent_message = await cai_chat.send_message(character_id, new_chat.chat_id, '\n'.join(message_history))
        # Removed because it shows an error with `turn`
        # discord2cai[str(message.channel.id)] = {
        #     'chatId': new_chat.chat_id,
        #     'firstMessageId': sent_message.id
        # }
        
        # with open('dc2cai.json', 'w') as file:
        #     json.dump(discord2cai, file)

        return sent_message.text
    
    # This part of the code will never get reached,
    # because if it does, it throws an error about not having `turn` for some reason..
    print('Found channel in memory')
    chat_info: dict[str, str] = discord2cai[str(message.channel.id)]
    edited_message = await cai_chat.edit_message(chat_info['chatId'], chat_info['firstMessageId'], '\n'.join(message_history))
    print(edited_message.text)
    return edited_message.text

async def load_char(char_id: str):
    global character_id, character_name
    
    character_name = (await cai_client.get_char(char_id)).name
    character_id = char_id
    
async def main() -> None:
    global cai_client, cai_chat, cai_me, character_name, discord2cai
    
    # Login and setup CharacterAI
    cai_client = aiocai.Client(getenv('CHARACTER_AI_TOKEN'))
    cai_me = await cai_client.get_me()
    cai_chat = await cai_client.connect()
    await load_char(character_id)
    print('CharacterAI Bot:', character_name)
    if file_exists('dc2cai.json'):
        discord2cai = json.load(open('dc2cai.json', 'r'))
    
    # Start Self-Discord Bot
    await create_task(dc_client.start(getenv('DISCORD_TOKEN')))

if __name__ == '__main__':
    run(main())
