import time
import random
import json
import datetime
import os
from tornado import websocket, web, ioloop
from datetime import timedelta
from random import randint

class WebSocketHandler(websocket.WebSocketHandler):

  # Addition for Tornado as of 2017, need the following method
  # per: http://stackoverflow.com/questions/24851207/tornado-403-get-warning-when-opening-websocket/25071488#25071488
  def check_origin(self, origin):
    return True

  #on open of this socket
  def open(self):
    print ('Connection established.')
    self.connectionOpen = True
    #ioloop to wait for 3 seconds before starting to send data
    ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=3), self.send_data)

 #close connection
  def on_close(self):
    print ('Connection closed.')
    self.connectionOpen = False

  def check_origin(self, origin):
    return True

  # Our function to send new (random) data for charts
  def send_data(self):
    print ("Sending Data")
    #create a bunch of random data for various dimensions we want
    value = random.randrange(-10,10) / 10.0

    #create a new data point
    measurement = {
    	'humidity': value,
        'pressure': value - 0.1,
        'roomTemp': value - 0.2,
        'temp1': value - 0.3,
        'temp2': value - 0.4,
        'temp3': value - 0.5
    }

    print (measurement)

    #write the json object to the socket
    if self.connectionOpen:
      try:
          self.write_message(json.dumps(measurement))
      except:
          print("An exception occured")

      #create new ioloop instance to intermittently publish data
      ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=1), self.send_data)

if __name__ == "__main__":
  #create new web app w/ websocket endpoint available at /websocket
  print ("Starting websocket server program. Awaiting client requests to open websocket ...")
  application = web.Application([(r'/static/(.*)', web.StaticFileHandler, {'path': os.path.dirname(__file__)}),
                                 (r'/websocket', WebSocketHandler)])
  application.listen(8001)
  ioloop.IOLoop.instance().start()
