#!/usr/bin/env python
import pika
import sys 
from PIL import Image
import io
import cv2

cam = cv2.VideoCapture (1, cv2.CAP_DSHOW)
reval, image = cam.read()
imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
img = Image.fromarray(imageRGB)
img.save("last_send_file.jpeg")
byteIO = io.BytesIO()
img = Image.open("last_send_file.jpeg")
img.save(byteIO, format='JPEG')
byteArr = byteIO.getvalue()
  
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.exchange_declare(exchange='topic', exchange_type='topic')
routing_key = sys.argv[1] if len(sys.argv) > 2 else 'anonymous.info'

channel.basic_publish(exchange='topic',routing_key=routing_key, body = byteArr)
print(" [Image] Sent %r" % (routing_key))
connection.close()


