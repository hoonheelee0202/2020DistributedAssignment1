import zmq
import time
import socket
#import mysql.connector
from middleware import db_connect
#from middleware import frontend

import pymysql.cursors

# Global Varible Declaration 
publisher = [] # topic, pid
subscriber = [] # topic, pid
search_list = [] # topic, pid

#--------------------------------------------------------------------
# Append the publisher to the list 'publisher'
# register_pub(topic,socket_id)
def append_publisher(topic,socket_id):
	publisher.append([topic,socket_id])

#--------------------------------------------------------------------
# Append the Subscriber to the list 'subscriber'
# register_sub(topic,socket_id)
def append_subscriber(topic,socket_id):
	subscriber.append([topic,socket_id])

def get_Host_name_IP(): 
	try: 
		host_name = socket.gethostname() 
		host_ip = socket.gethostbyname(host_name) 
		print("Hostname :  ",host_name) 
		print("IP : ",host_ip) 
	except: 
		print("Unable to get Hostname and IP") 

def main():
	print("Broker started..")


  
	# Function to display hostname and 	
	# IP address 

  
	# Driver code 
	get_Host_name_IP() #Function call 

	search_list = []

	mydb = db_connect()

	mycursor = mydb.cursor()

	# Table Initialization
	mycursor.execute("DELETE FROM publisher")
	mycursor.execute("DELETE FROM subscriber")


	# Prepare our context and sockets
	context = zmq.Context()
	frontend = context.socket(zmq.ROUTER)
	frontend.bind("tcp://*:5559")

	# Initialize poll set
	poller = zmq.Poller()
	poller.register(frontend, zmq.POLLIN)

	
	message_type = "0"

	# Switch messages between sockets
	while True:
		#print("While true")
		socks = dict(poller.poll())
		
		#print("socks.get before")
		if socks.get(frontend) == zmq.POLLIN:
			#print("socks.get after")
			message = frontend.recv_multipart()
			
			message_type = message[2].decode()
			socket_id = message[3].decode()
			topic = message[4].decode()

			print("Received msg_type: "+message_type+", socket_id: "+socket_id+", topic: "+topic)
			
			if message_type == "1" : # request to register the publisher
				append_publisher(topic, socket_id)
				# DB Insert to the table 'publisher'
				sql = "INSERT INTO publisher VALUES (%s, %s)"
				val = (topic, socket_id)
				mycursor.execute(sql, val)
				mydb.commit()
				print("\nInsert into publisher("+topic+","+socket_id+")")
				#print "SQL execution: "+sql
				# send bakc the reply
				frontend.send_multipart([socket_id.encode(),b"",b"Thank you 1"])
			elif message_type == "2" :  # request to register the subscriber
				append_subscriber(topic, socket_id)
				# DB Insert to the table 'subscriber'
				mycursor = mydb.cursor()
				sql = "INSERT INTO subscriber VALUES (%s, %s)"
				val = (topic, socket_id)
				mycursor.execute(sql, val)

				mydb.commit()
				print("\nInsert into subscriber("+topic+","+socket_id+")")
				# send bakc the reply
				frontend.send_multipart([socket_id.encode(),b"",b"Thank you 2"])
			elif message_type == "3" :
				#search_list = find_brute(subscriber, topic)
				print("\nBroker publishing the message..")
				mycursor = mydb.cursor()
				sql = "SELECT * FROM subscriber WHERE topic='"+topic+"'"
				#print(sql)

				mycursor.execute(sql)
				myresult = mycursor.fetchall()
				
				#print "Len of myresult"+str(len(myresult))
				if len(myresult)!=0 : # Add the searched DB result to the search_list
					for x in myresult:
						search_list.append([x[0],x[1]])
					contents = str(message[5])

					# send the return Messages to the subscribers
					for i in range(len(search_list)):
						return_socket_id = "Wait"+search_list[i][1] #Make the socket_id by adding "Wait" to the front
						#print("return topic: "+topic+", return socket: "+return_socket_id)
						frontend.send_multipart([return_socket_id.encode(),b"",contents.encode()])
						frontend.send_multipart([socket_id.encode(),b"",b"Thank you 3"])
					
					# Initialize the search_list
					search_list = []
				else:
					print("\nNo matched subscriber to receive the contents")
					frontend.send_multipart([socket_id.encode(),b"",b"Thank you 3"])
					

if __name__ == "__main__":
	main()
