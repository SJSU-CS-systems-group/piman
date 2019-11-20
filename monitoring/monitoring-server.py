from sys import argv
import time

from flask import Flask
from flask_restful import Api, Resource, reqparse
import psutil

app = Flask(__name__)
api = Api(app)

events = []

class Pimon(Resource):
    def get(self):
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory()[2]
        disk_percent = psutil.disk_usage('/')[3]
        num_pids = len(psutil.pids())
        temperature = psutil.sensors_temperatures().get('cpu-thermal')[0][1]

        event = {
            "time": time.time(),
            "cpu_percent":    cpu_percent,
            "memory_percent": memory_percent,
            "disk_percent":   disk_percent,
            "num_pids":       num_pids,
            "temp":           temperature,
        }
        events.append(event)
        return event, 200
      
api.add_resource(Pimon, "/event/")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port="3000")
