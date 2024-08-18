# Demo video

[![Watch the video](https://img.youtube.com/vi/7pSMZXBBb-c/hqdefault.jpg)](https://www.youtube.com/watch?v=7pSMZXBBb-c)

[Watch the demo video on YouTube](https://www.youtube.com/watch?v=7pSMZXBBb-c)

# Features working:
1. Signup and that adds the user to the central users table. July 28th 2024
2. Login and that logs in the user and creates the personal DB for the user. July 28th 2024
3. Set the OAI model and key and that gets saved to the central users DB. July 28th 2024
4. Able to add/edit the asset from the UI. This updates the DB and updates the ROW_START and ROW_END values. July 28th 2024
5. Able to chat with the AI from the investnment guru tab. July 28th 2024.
6. Editing basic memory works. July 29th 2024.

# How to run locally?

## For the webapp

### On a windows 11


### On a mac with a fish shell

> cd platform/webapp/ui

> brew install yarn

> brew install nodejs

> yarn install

> set -x NODE_ENV development 
1. Since I am using fish shell. If you are using a different shell use your shell specific command to set the environment variable.
2. This will redirect API calls to local python

> yarn dev

## For the api

### On a mac with a fish shell

> cd platform/api

> python3 -m venv python3-venv    <- This creates the virutal environment for the python

> source python3-venv/bin/activate.fish <- I use the fish shell

> which python3
/Users/vk/code/platform/api/python3-venv/bin/python3

> which pip3
/Users/vk/code/platform/api/python3-venv/bin/pip3

> set -x SERVER_ENV development
1. This will enable CORS on localhost
2. Sets the database path to 'data/dev/'

> pip3 install -r requirements.txt

(python3-venv) vk@vks-macbook-pro ~/c/p/api (main)> python3 ai-request.py 
 * Serving Flask app 'ai-request'
 * Debug mode: on
INFO:werkzeug:WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:3003
 * Running on http://192.168.87.116:3003
INFO:werkzeug:Press CTRL+C to quit
INFO:werkzeug: * Restarting with stat
WARNING:werkzeug: * Debugger is active!
INFO:werkzeug: * Debugger PIN: 966-690-146

## to check the DB

### On a mac with a fish shell

brew install --cask db-browser-for-sqlite
