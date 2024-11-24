import discord
from characterai import aiocai
from dotenv import load_dotenv; load_dotenv()
from os import getenv
from asyncio import run, create_task, wait
import json
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

MESSAGE_SUFFIX = '\n-# This message was made with AI'

@dc_client.event
async def on_ready() -> None:
    print(f"Finished logging in as {dc_client.user}!")

@dc_client.event
async def on_message(message: discord.Message) -> None:
    if message.author == dc_client.user or not (isinstance(message.channel, discord.channel.DMChannel) or dc_client.user in message.mentions):
        return
    
    print('Received message')
    await wait(uniform(2.0, 6.0))  # More human like?
    async with message.channel.typing():
        await message.reply(await reply_to_discord(message) + MESSAGE_SUFFIX)

async def reply_to_discord(message: discord.Message) -> None:
    try:
        print('Loading message history...')
        previous_messages: list[str] = []
        async for msg in message.channel.history(oldest_first=True):
            if msg.author != dc_client.user:
                # TODO: Convert <@> to actual usernames
                previous_messages.append(f'{msg.author.name}: {msg.content}')
                continue
            
            previous_messages.append(f'{character_name}: {msg.content.replace(MESSAGE_SUFFIX, "")}')
        
        if str(message.channel.id) not in discord2cai:
            print(f'Channel {message.channel} isn\'t in memory, adding...')
            new_chat, _ = await cai_chat.new_chat(character_id, cai_me.id)
            sent_message = await cai_chat.send_message(character_id, new_chat.chat_id, '\n'.join(previous_messages))
            # Removed because it shows an error with `turn`
            # discord2cai[str(message.channel.id)] = {
            #     'chatId': new_chat.chat_id,
            #     'firstMessageId': sent_message.id
            # }
            
            with open('dc2cai.json', 'w') as file:
                json.dump(discord2cai, file)

            return sent_message.text
        
        # This part of the code will never get reached,
        # because if it does, it throws an error for some reason..
        print('Found channel in memory')
        chat_info: dict[str, str] = discord2cai[str(message.channel.id)]
        edited_message = await cai_chat.edit_message(chat_info['chatId'], chat_info['firstMessageId'], '\n'.join(previous_messages))
        print(edited_message.text)
        return edited_message.text
    except Exception as e:
        print(e)
    
    

async def main() -> None:
    global cai_client, cai_chat, cai_me, character_name, discord2cai
    
    # Login and setup CharacterAI
    cai_client = aiocai.Client(getenv('CHARACTER_AI_TOKEN'))
    cai_me = await cai_client.get_me()
    cai_chat = await cai_client.connect()
    character_name = (await cai_client.get_char(character_id)).name
    if file_exists('dc2cai.json'):
        discord2cai = json.load(open('dc2cai.json', 'r'))
    
    # Start Self-Discord Bot
    await create_task(dc_client.start(getenv('DISCORD_TOKEN')))

if __name__ == '__main__':
    run(main())