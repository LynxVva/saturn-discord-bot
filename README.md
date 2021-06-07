# Saturn
A multipurpose discord bot made in python.

# Invite the bot
[Click here](https://discord.com/oauth2/authorize?client_id=799328036662935572&permissions=8&scope=bot)

# Self Hosting
Self hosting is generally not recommended, but this might change in the future. For now, please invite the bot with the link above.

# Contributing
If you decide you do want to contribue, then your contribution is appreciated.
Below are the steps to get the repository set up.
```
$ git clone https://github.com/Synchronous/saturn
$ cd saturn
$ py -3 -m pip install -r requirements.txt
$ py -m pip venv venv
```
Create a file named .env, and paste in the follow information. Remember to remove the <>!
```
TOKEN=<your token here>
MONGO=<your mongo uri here>
OWNERIDS=<your owner ids here, separated by spaces>
```

# Requirements
|Package   |Version   |
|---|---|
|discord.py     |~=1.7.2 |
|motor          |~=2.4.0 | 
|python-dotenv  |~=0.15.0| 
|pytimeparse    |~=1.1.8 | 
|aiohttp        |~=3.7.4 | 
|Pillow         |~=8.2.0 | 
|pytz           |~=2021.1|
|python-dateutil|~=2.8.1 |
|mystbin.py     |~=2.1.3 |
