from flask import Flask, request
import requests
from bot import *

app = Flask(__name__)
robot = Robot(10)
ACCESS_TOKEN = "EAAEUY1nxzTEBAAlfrs3CrXTwUYjwfTA93cAFgBQcfhjHeRCi20t8k31P5jEDMXcmZB8gXYhMkDLSZAateRdNQHO0P55mgcWXbSlW6wKj7TWxO0dYzIPZBET8WChpEgFIVyrFtHnxZA26DWYZBAoud3X9Hgshw62IZCxBE4PrAGHwZCEhcB0eiQK"


def reply(user_id, msg):
    data = {
        "recipient": {"id": user_id},
        "message": {"text": msg}
    }
    resp = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + ACCESS_TOKEN, json=data)
    print(resp.content)

@app.route('/', methods=['GET'])
def handle_verification():
    return request.args['hub.challenge']

@app.route('/', methods=['POST'])
def handle_incoming_messages():
    data = request.json
    if 'messaging' not in data['entry'][0]:
        return 'ok'
    sender = data['entry'][0]['messaging'][0]['sender']['id']
    message = data['entry'][0]['messaging'][0]['message']['text']
    reply(sender, robot.command(message))
    return "ok"


if __name__ == '__main__':
    app.run(debug=True)