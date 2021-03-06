#
#   Request-reply client in Python
#   Connects REQ socket to tcp://localhost:5559
#   Sends "Hello" to server, expects "World" back
#
import zmq
import os
import random
import threading
import time
from middleware import register_sub
from middleware import connect
from middleware import wait_for_published_topic

import argparse   # argument parser


##################################
# Command line parsing
##################################
def parseCmdLineArgs ():
    # parse the command line
	parser = argparse.ArgumentParser ()

    # add positional arguments in that order
	parser.add_argument ("mode", help="1:Just Register the subscriber, 2:Register the subscriber and start listeng to the topic")
	parser.add_argument ("ipaddress")
	parser.add_argument ("portnumber")

    # parse the args
	args = parser.parse_args ()

	return args


def main():
	print("Subscriber Main Function started..")

	# first parse the command line arguments
	parsed_args = parseCmdLineArgs ()

	# Get the process id of the process to use as the unique socket ID
	pid = os.getpid()
	pid_str = str(pid)

	# Topic is randomly chosen
	topic = random.choice(["sports", "music", "weather"])
	print("Process ID:"+pid_str+", Interested Topic : "+topic)

	#brokeraddressIP = raw_input("Enter the broker's IP address(e.g. 10.0.2.15) : ") 
	#brokeraddressPort = raw_input("Enter the broker's PORT address(e.g. 5559) : ") 
	brokeraddressIP = parsed_args.ipaddress
	brokeraddressPort = parsed_args.portnumber
	brokeraddress = "tcp://"+brokeraddressIP+":"+brokeraddressPort

	# register the subscriber to the broker
	#print("Register Subscriber(topic: "+str(topic)+", process id: "+pid_str+", brokeraddress: "+brokeraddress+")")
	#result = register_sub(topic,pid_str,brokeraddress)
	register_sub(topic,pid_str,brokeraddress)
	#print("Register Subscriber ended")

	if parsed_args.mode=="D": # Directly receive the messages from the publishers
		context = zmq.Context()
		socket = context.socket(zmq.REP)
		bind_address = "tcp://*:"+pid_str
		socket.bind(bind_address)

		while True:
			print("\nWait on  socket.recv_multipart()")
			message = socket.recv()
			print("Directly received message: "+message.decode())
			socket.send(b"Thank you publisher")

	#if parsed_args.mode<>"D":
	else: # if argument is not 'D' then start waiting for the published contents
		pid_str = "Wait"+pid_str # make the socket identification by adding "Wait" to the front of the process id
		#print("connect to the broker: "+brokeraddress)
		connect(pid_str, brokeraddress) # connect to the Broker

		while True:
			message = wait_for_published_topic()
			print("Published Contents: "+str(message[1]))


if __name__ == "__main__":
	main()
