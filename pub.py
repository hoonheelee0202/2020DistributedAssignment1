import zmq
import os
import random
import threading
import time
from middleware import register_pub
from middleware import register_sub
from middleware import publish
from middleware import db_connect
#from broker import frontend

import argparse   # argument parser

# Global Varible Declaration 
search_list = [] # topic, pid


##################################
# Command line parsing
##################################
def parseCmdLineArgs ():
    # parse the command line
    parser = argparse.ArgumentParser ()

    # add positional arguments in that order
    parser.add_argument ("mode", help="D:Directly send the contents to the subscriber, 2:Send the contents to the broker")

    # parse the args
    args = parser.parse_args ()

    return args

def main():
	# Initialize the search_list
	search_list = []

	# Prepare our context and sockets
	context = zmq.Context()

	print "Publisher Main Function started.."

	# first parse the command line arguments
	parsed_args = parseCmdLineArgs ()
	
	# Get the process id of the process to use as the unique socket ID
	pid = os.getpid()
	pid_str = str(pid)

	print "Process ID:"+pid_str

	first_flag=True

	# Topic is randomly chosen
	###topic = random.choice([b"sports", b"music", b"weather"])
	###print "publishing Topic: "+topic
	
	# Contents is randomly chosen
	###contents = random.choice([b"Good morning", b"Good Afternoon", b"Good Evening"])
	###print "publishing Contents: "+contents

	
	
	# Register the publisher to the Broker
	### register_pub(topic,pid_str)

	# Publish the contents
	if parsed_args.mode == "D":
		print "Directly send the contents to Subscribers without going through broker"
		
		while True:

			topic = raw_input("Enter the topic : ") 
			contents = raw_input("Enter the contents : ")

			if first_flag == True:
				register_pub(topic,pid_str) # Register the publisher to the broker
				first_flag = False
			
			mydb = db_connect()
			mycursor = mydb.cursor()
			sql = "SELECT * FROM subscriber WHERE topic='"+topic+"'"
			print "SQL: "+sql
			mycursor.execute(sql)
			myresult = mycursor.fetchall()
			for x in myresult:
				print x
				search_list.append([x[0],x[1]])

			print "search_list"
			print search_list

			# send the return Messages to the subscribers
			for i in range(len(search_list)):
				connect_address ="tcp://localhost:"+search_list[i][1]
				print "connect_address: "+connect_address
				socket = context.socket(zmq.REQ)
				socket.connect(connect_address)		
				#return_socket_id = "Wait"+search_list[i][1]
				
				socket.send(contents.encode())
				message = socket.recv()
				print "Returned message: "+message
				socket.close()
			
			# Initialize the search_list
			search_list = []
			mycursor.close()
			mydb.close()

	else:
		# send the contents to Subscribers using the Broker
		while True:
			topic = raw_input("Enter the topic : ") 
			contents = raw_input("Enter the contents : ")

			if first_flag == True:
				register_pub(topic,pid_str) # Register the publisher to the broker
				first_flag = False

			print "\n\nPublish the contents to the subscribers\n"
			publish(topic,pid_str,contents)

if __name__ == "__main__":
	main()

