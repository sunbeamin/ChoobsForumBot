## Installation
* Install git `sudo apt-get install git`
* Clone the git repo of the Python Discord bot `git clone https://github.com/MarijnStam/ChoobsForumBot.git`
* Install python3 `sudo apt-get install python3`
* Install python venv `sudo apt-get install python3.9-venv` ****Only needed if on Debian/Ubuntu systems
* Create a Python Virtual Enviroment `python3 -m venv /path/to/wherever`
* cd to the `bin/` directory in the python virtual enviroment 
* Add the following lines at the bottom of the `activate` file (the one without extensions)

	`export DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN_HERE` <br />
    `export DISCORD_CHANNEL=DESIRED_DISCORD_CHANNEL_ID_HERE`

* Replace `YOUR_DISCORD_BOT_TOKEN_HERE` with your bot token, no need for {} or [] etc
* Replace `DESIRED_DISCORD_CHANNEL_ID_HERE` with the ID of the channel that you want the bot to send messages to

* Activate the Python venv `source /path/to/your/venv/bin/activate`
* Install the necessary requirements `pip install -r requirements.txt`



## Running the bot
* Activate the Python venv if not already active `source /path/to/your/venv/bin/activate`
* *IMPORTANT:* Navigate to the directory of the Choobsbot e.g. in my case:  `cd Desktop/ChoobsForumBot/`
* Run the discordBot.py file from the venv `python3 discordBot.py`

The bot will check the forum for new posts every 60 seconds by default, if a new message is posted, it will be posted to the Discord Channel.
It should be resilient to internet outages and file errors etc. 
Feel free to DM me for any concerns/questions
