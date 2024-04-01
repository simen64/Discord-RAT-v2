# Discord RAT V2

A remote access tool through Discord. Including for now 10+ exploitation modules including, Linux sudo phishing, duckyscript support, clipboard monitor and more. See full list if commands [here](help_menu.md).

## Warning

Use this responsibly and ethically. Do not use on any unauthorized targets. I am not liable for any harm or / damage done with this tool.

## Dependencies

- Python 3.1 or higher with required libraries (see getting started)
- Linux or Windows, the tool will auto detect if its windows or linux and enable the OS dependent functions. If any other OS is detected it will just exit the program.

It does currently not support wayland, this will be fixed in the future.

## Getting Started

### The Attacker

To get started on the attacker side, you have to follow these steps:

1. Create a discord server with only you in. (Any person in the discord server will have access to your targets computer)
2. Set up a Discord Bot:
- Go to the [Discord Developer Portal](https://discord.com/developers/applications).
- Click "New Application" and give it a name (e.g., "RAT Bot").
- Navigate to the "Bot" section
- Under the "Token" section, reset your token, then click "Copy" to copy your bot token.
- Keep this token secure you will need it later
- Scroll down and enable the `Message Content Intent` switch
- Save your changes
- Navigate to the OAuth2 page, then URL Generator
- Select the `bot` scope
- Enable the required permissions like: `Send messages`, `Attach files`, `Read messages`, `Read message history`, `Embed Links`, and others you might need.
- Copy the URL at the bottom, paste it in your browser and add the bot to the server **WITH ONLY YOU IN**

Now you as the attacker is ready to deploy.

### The target

Heres how to deploy on your target.

1. Clone the repo or download the [RAT-V2.py](RAT-V2.py) file. (It is recommended to put this in a folder)
2. In the same directory create a file called `.env`
3. In this file add thiese two lines:  
```
DISCORD_TOKEN=the token you gained earlier
```  
```
CHANNEL=your channel id
```
You can get your channel id by enabling developer mode in Discord settings, then right clicking your discord channel and pressing `Copy Channel ID`  

4. Save the file and close it
5. Install the needed libraries:
```python -m pip install -r https://raw.githubusercontent.com/simen64/Discord-RAT-v2/main/requirements.txt``` (`python3` if your on Linux)
6. Run `RAT-V2.py`!

Now if you have access to your targets terminal output of `RAT-V2.py` you should see this when the program has started: `Logged in as: Your bot`

### Other ways to deploy

The previous steps are the original way too deploy which you can use to package in your payload.
But i have also made a premade payloads to deliver it with just a file / command.  
I will make more in the future.

[Bash command](Deploy-script-bash.sh) Run this with your discord token as the command argument, like this: `bash Deploy-script-bash.sh discord-token`

## Usage

In the discord server you invited your bot to you can access the help menu which lists all exploitation modules with `!help`

## Feature requests?

Open a issue!

## Want to help develop?

Contact me as i have not set up a concrete way for this yet
