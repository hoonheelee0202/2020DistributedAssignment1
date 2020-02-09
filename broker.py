import zmq
import time
import mysql.connector
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

def find_brute(list, topic):
	result = []
	for index, sublist in enumerate(list):
		if sublist[0] == topic:
			result.append(index);

	return result

def main():
	print "Broker started.."

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
		socks = dict(poller.poll())

		if socks.get(frontend) == zmq.POLLIN:
			message = frontend.recv_multipart()
			
			message_type = message[2]
			socket_id = message[3]
			topic = message[4]

			print "Received msg_type: "+message_type+", socket_id: "+socket_id+", topic: "+topic
			
			if message_type == "1" : # request the register the publisher
				append_publisher(topic, socket_id)
				# DB Insert to the table 'publisher'
				sql = "INSERT INTO publisher VALUES (%s, %s)"
				val = (topic, socket_id)
				mycursor.execute(sql, val)

				mydb.commit()
				print "\nInsert into publisher("+topic+","+socket_id+")"
				#print "SQL execution: "+sql
				# send bakc the reply
				frontend.send_multipart([socket_id.encode(),"",b"Thank you 1"])
			elif message_type == "2" :
				append_subscriber(topic, socket_id)
				# DB Insert to the table 'publisher'
				mycursor = mydb.cursor()
				sql = "INSERT INTO subscriber VALUES (%s, %s)"
				val = (topic, socket_id)
				mycursor.execute(sql, val)

				mydb.commit()
				print "\nInsert into subscriber("+topic+","+socket_id+")"
				# send bakc the reply
				frontend.send_multipart([socket_id.encode(),"",b"Thank you 2"])
			elif message_type == "3" :
				#search_list = find_brute(subscriber, topic)
				print "\nBroker publishing the message.."
				mycursor = mydb.cursor()
				sql = "SELECT * FROM subscriber WHERE topic='"+topic+"'"
				print sql

				mycursor.execute(sql)
				myresult = mycursor.fetchall()
				
				#print "Len of myresult"+str(len(myresult))
				if len(myresult)<>0 : 	
					for x in myresult:
						search_list.append([x[0],x[1]])
					contents = message[5]


					# send the return Messages to the subscribers
					for i in range(len(search_list)):
						return_socket_id = "Wait"+search_list[i][1]
						print "return topic: "+topic+", return socket: "+return_socket_id 
						frontend.send_multipart([return_socket_id.encode(),"",contents.encode()])
						frontend.send_multipart([socket_id.encode(),"",b"Thank you 3"])
					
					# Initialize the search_list
					search_list = []
				else:
					print "\nNo matched subscriber to receive the contents"
					frontend.send_multipart([socket_id.encode(),"",b"Thank you 3"])
					

if __name__ == "__main__":
	main()