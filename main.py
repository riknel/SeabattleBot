from flask import Flask, request
import requests
from bot import *
import json
import logging
import random
logging.basicConfig(filename="info.log", filemode='w', level=logging.DEBUG)

app = Flask(__name__)
robot = Robot(10)
ACCESS_TOKEN = "EAAEUY1nxzTEBAAlfrs3CrXTwUYjwfTA93cAFgBQcfhjHeRCi20t8k31P5jEDMXcmZB8gXYhMkDLSZAateRdNQHO0P55mgcWXbSlW6wKj7TWxO0dYzIPZBET8WChpEgFIVyrFtHnxZA26DWYZBAoud3X9Hgshw62IZCxBE4PrAGHwZCEhcB0eiQK"
VER_CODE = "secret"
stickers = ["^_^", ":)", ";)", ":|", ":/", ":(", ":o", "o_o"]

def reply(user_id, msg):
    data = {
        "recipient": {"id": user_id},
        "message": {"text": msg}
    }
    resp = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + ACCESS_TOKEN, json=data)
    if resp.status_code == requests.codes.ok:
        logging.info(resp.content)
    else:
        logging.error(resp.content)

@app.route('/', methods=['GET'])
def handle_verification():
    logging.info("Handle verification")
    if request.args["hub.verify_token"] == VER_CODE:
        logging.info("Verification successful")
        return request.args['hub.challenge']
    else:
        logging.critical("Verification failed")
        return 'Error, wrong validation token.'

@app.route('/', methods=['POST'])
def handle_incoming_messages():
    logging.info("Incoming messages...")
    data = request.get_data()
    for sender, message in handle_data(data):
        if sender is None:
            logging.error("Empty sender.")
            continue
        elif message is None:
            logging.info("Sticker!")
            reply(sender, random.choice(stickers))
            continue
    try:
        logging.info("Bot message")
        reply(sender, robot.command(message))
    except Exception as e:
        logging.error("Unexpected error.")
    return "ok"

#Пример сообщения
#{'object': 'page', 'entry': [{'id': '160904671107139', 'time': 1494157071673, 'messaging': [{'sender': {'id': '1300267486725167'}, 'recipient': {'id': '160904671107139'}, 'timestamp': 1494157071559, 'message': {'mid': 'mid.$cAADIoWQ2PB1iE_jcx1b4rOUeIpZf', 'seq': 1916, 'text': '1 b'}}]}]}
#b'{"recipient_id":"1300267486725167","message_id":"mid.$cAADIoWQ2PB1iE_jgfVb4rOYS4Pfg"}'

def handle_data(data):
    info = json.loads(data)
    if 'entry' not in info or 'messaging' not in info['entry'][0] or 'sender' not in info['entry'][0]['messaging'][0]:
        return
    messages = info['entry'][0]['messaging']
    for event in messages:
        if "message" in event and "text" in event["message"]:
            yield event["sender"]["id"], event["message"]["text"]
        elif "sender" in event:
            yield event['sender']["id"], None

if __name__ == '__main__':
    app.run(debug=True)

