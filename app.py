from flask import Flask, render_template
from datetime import datetime
from pusher import Pusher
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import requests
import time
import atexit
import os


pusher = Pusher(
	app_id = '694790',
	key = '16aabf8c06362b1e9be5',
	secret = '54988777ebc2c9fc7641',
	cluster = 'eu',
	ssl=True
	)


app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('base.html')

x = []
y = []

def func():
	global x, y
	response = requests.get('https://api.openweathermap.org/data/2.5/weather?q=Brno&APPID=be0aff8ecd9cc5141540bc38f8641a4b&units=metric').json()
	t = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	x.append(t)
	y.append(response['main']['temp'])
	x = x[-10:]
	y = y[-10:]
	pusher.trigger('my-channel', 'my-event', {'x': x, 'y': y})
	pusher.trigger('channel', 'event', y[-1])


scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    func=func,
    trigger=IntervalTrigger(seconds=10),
    id='prices_retrieval_job',
    name='Retrieve prices every 10 seconds',
    replace_existing=True)
# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


if __name__ == '__main__':
     app.debug = True
     port = int(os.environ.get("PORT", 5000))
     app.run(host='0.0.0.0', port=port)