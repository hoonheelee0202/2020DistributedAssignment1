import os
import sys
import zmq
import time
import pymysql.cursors
#import mysql.connector

""" Global Variables for Main Program """
# Prepare our context and sockets
#context = zmq.Context()
#frontend = context.socket(zmq.ROUTER)

#BrokerAddress = "tcp://localhost:5559"
context1 = zmq.Context()
socket1 = context1.socket(zmq.REQ)
context2 = zmq.Context()
socket2 = context2.socket(zmq.DEALER)

#--------------------------------------------------------------------
# register the publisher function
# register_pub(topic,socket_id)
def register_pub(topic,socket_id,brokeraddress):
	#print("Register_pub function starts")
	socket1.setsockopt(zmq.IDENTITY, socket_id.encode()) # set the id of the socket
	socket1.connect(brokeraddress) # connect
	# send the msg to the broker("1" is for the registering the publisher
	socket1.send_multipart([b"1",socket_id.encode(),topic.encode()])
	#print("Register message('1') sent")
	result = socket1.recv_multipart()
	#print("Register_pub result:"+result)

	return result

#--------------------------------------------------------------------
# register the subscriber function
# register_sub(topic,socket_id)
def register_sub(topic,socket_id,brokeraddress):

	#print("\n\nReigster Subscriber Function started: "+brokeraddress)
	socket1.setsockopt(zmq.IDENTITY, socket_id.encode()) # set the id of the socket
	socket1.connect(brokeraddress) # connect

	#print("connect")
	# send the msg to the broker("2" is for the registering the subscriber
	socket1.send_multipart([b"2",socket_id.encode(),topic.encode()])
	#socket1.send_multipart([str("2"),socket_id,topic])
	#print("send")
	result = socket1.recv_multipart()
	#print("recv_multipart: "+str(result))
	return result


#--------------------------------------------------------------------
# publish the topic to the subscribers interested
# publish(topic, socket_id):
def publish(topic,socket_id,contents):
	#print("publish function starts")
	socket1.send_multipart([b"3",socket_id.encode(),topic.encode(),contents.encode()])
	#print("publish message('3') sent")
	message = socket1.recv_multipart()
	#print message
	return message



#--------------------------------------------------------------------
# Make the connection to the router as a DEALER
# connect(socket_id)
def connect(socket_id,brokeraddress):
	socket2.setsockopt(zmq.IDENTITY, socket_id.encode())  # set the id of the socket
	#print("\n\nConnect to the broker with the Socket_ID("+socket_id+")")
	socket2.connect(brokeraddress) # connect

#--------------------------------------------------------------------
# The subscribers wait for the topic to be published
# wait_for_published_topic(topic,socket_id)
def wait_for_published_topic():
	# Wait for the published topic
	result = socket2.recv_multipart()
	
	return result

#--------------------------------------------------------------------
# Database Connection
# db_connect()
def db_connect():
	#print("db connection started..")
	# Database Connect
	mydb = pymysql.connect(
	#mydb = mysql.connector.connect(
		host="localhost",
		user="lhh",
		passwd="1234",
		database="pubsub"
	)

	return mydb




