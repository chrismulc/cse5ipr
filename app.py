
"""

A small Test application to show how to use Flask-MQTT.

"""
import logging

import eventlet
import json
from flask import Flask, render_template, redirect, url_for
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message

eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET'] = 'my secret key'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MQTT_BROKER_URL'] = 'broker.hivemq.com'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_CLIENT_ID'] = 'flask_mqtt'
app.config['MQTT_CLEAN_SESSION'] = True
app.config['MQTT_USERNAME'] = ''
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False
app.config['MQTT_LAST_WILL_TOPIC'] = 'home/lastwill'
app.config['MQTT_LAST_WILL_MESSAGE'] = 'bye'
app.config['MQTT_LAST_WILL_QOS'] = 2

app.config['SERVER_NAME'] = "0.0.0.0:5000"

app.config.update(
    DEBUG=True,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_TLS=False,
    MAIL_USE_SSL=True,
    MAIL_USERNAME= os.environ.get('MAIL_USERNAME'),
    MAIL_PASSWORD= os.environ.get('MAIL_PASSWORD')
)

mail = Mail(app)

mqtt = Mqtt(app)
socketio = SocketIO(app)
bootstrap = Bootstrap(app)


@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('publish')
def handle_publish(json_str):
    data = json.loads(json_str)
    mqtt.publish(data['topic'], data['message'], data['qos'])


@socketio.on('subscribe')
def handle_subscribe(json_str):
    data = json.loads(json_str)
    mqtt.subscribe(data['topic'], data['qos'])


@socketio.on('unsubscribe_all')
def handle_unsubscribe_all():
    mqtt.unsubscribe_all()


def manual_email():
    with app.app_context():
        try:
            msg = Message("Warning: CPU Usage",
                sender="chrismulcair@gmail.com",
                recipients=["chrismulcair@gmail.com"])
            msg.body="CPU Usage above 50%"
            mail.send(msg)
            return 'Mail sent!'
            print("Sent")
        except Exception as e:
            return (str(e))

def manual_email2():
    with app.app_context():
        try:
            msg = Message("Warning: Memory Usage",
                sender="chrismulcair@gmail.com",
                recipients=["chrismulcair@gmail.com"])
            msg.body="Memory Usage above 80%"
            mail.send(msg)
            return 'Mail sent!'
            print("Sent")
        except Exception as e:
            return (str(e))

@app.route('/send-mail/')
def send_mail():
    try:
        msg = Message("Send Mail Tutorial",
          sender="chrismulcair@gmail.com",
          recipients=["chrismulcair@gmail.com"])
        msg.body="Testing"
        mail.send(msg)
        return 'Mail sent!'
        print("Sent")
    except Exception as e:
        return (str(e))

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode(),
        qos=message.qos,
    )

    real_topic = str(data["topic"])
    socketio.emit('mqtt_message', data=data)
    #if data["payload"] == "ON":
    if real_topic == 'topic/cpu_reply/messages' and float(data["payload"]) > 50:
        manual_email()
    if real_topic == 'topic/mem_reply/messages' and float(data["payload"]) > 60:
        manual_email2()

@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    # print(level, buf)
    pass


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, debug=True)
