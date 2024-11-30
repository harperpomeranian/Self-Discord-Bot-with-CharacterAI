# Self Discord Bot with Character AI

Simple setup, just define your variables in .env and you'll be done!

## Installation and Usage

After cloning this repo onto your machine, follow these steps:

### Step 1: Install requirements
Create a virtual environment, then install the required packages by running `pip install -r requirements.txt`

### Step 2: Get your CharacterAI Token

1. Run [get_character_ai_token.py](./get_character_ai_token.py) and follow the instructions.
2. Copy your token and paste it into your `.env` file

### Step 3: Get your Discord token

1. Open Discord on your browser, make sure you're logged in.
2. Open Developer tools by clicking F12 or right-clicking on the page and selecting "Inspect".
3. Run this code in the console:
    ```javascript
    // From: https://stackoverflow.com/a/69868564/23834759

    (webpackChunkdiscord_app.push([[''],{},e=>{m=[];for(let c in e.c)m.push(e.c[c])}]),m).find(m=>m?.exports?.default?.getToken!==void 0).exports.default.getToken()
    ```
4. Copy your token then paste it into your `.env` file

### Step 4: Get your CharacterAI bot's ID

1. Visit [old.character.ai](https://old.character.ai) and login. Go to your bot and copy the bot's ID from the url.
    > **Example**
    >
    > **Url**: https://character.ai/chat/_20YpNNtOgwmdCTaCc-BrHvVdH09DimZDGWX62PyxJ8<br/>
    > **Bot ID**: _20YpNNtOgwmdCTaCc-BrHvVdH09DimZDGWX62PyxJ8
2. Save the Bot ID in the `.env` file

### Step 5: Run the bot

- This is the final step
- Run [main.py](./main.py) and wait for the bot to start!

### More: What the .env file must look like

Get your discord token, character AI token, and your character AI's bot id. Then put them all in a `.env` file in the root directory.

```env
DISCORD_TOKEN="<Your Discord Token>"
CHARACTER_AI_TOKEN="<Your C.AI token>"
CHARACTER_ID="<Character ID>"
```

## Custom commands

There's some built-in custom commands that I've added, but you can remove them or even add your own

- `-!botset <Bot ID>`<br/>
    - Changes the current bot
- `-!refresh`
    - Refreshes configuration (whitelist)

## Where EXE?

- The bot is a python script, so you'll need to run it with python
- And plus, it's simple enough to understand the steps to run this

<hr/>

<p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/harperpomeranian/Self-Discord-Bot-with-CharacterAI">Self Discord Bot with CharacterAI</a> by <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://github.com/harperpomeranian">Harper Pomeranian</a> is licensed under <a href="https://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">CC BY 4.0<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1" alt=""><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1" alt=""></a></p>