
import SocketServer, threading, time
import paho.mqtt.client as mqtt #import the client1
import sqlite3
from sqlite3 import Error

count = 1
host_part = ""
number_part = ""


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def create_project(conn, project):
    sql = ''' INSERT INTO projects(Sensor_ID)
    VALUES(?) '''
    cur = conn.cursor()
    cur.execute(sql, project)
    conn.commit()

    return cur.lastrowid

def create_project2(conn, project):
    sql = ''' INSERT INTO projects2(Sensor_ID)
    VALUES(?) '''
    cur = conn.cursor()
    cur.execute(sql, project)
    conn.commit()

    return cur.lastrowid



def select_all_projects(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM projects")

    rows = cur.fetchall()

    for row in rows:
        print(row)

def select_all_projects2(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM projects2")

    rows = cur.fetchall()

    for row in rows:
        print(row)



def query_db(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM projects WHERE Humidity < 60")

    rows = cur.fetchall()

    for row in rows:
        print(row)

def get_last_10_records(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM projects ORDER BY Sensor_ID DESC LIMIT 10")

    rows = cur.fetchall()

    print("********************** L A S T 10 RECORDS ***************************")
    for row in rows:
        client.publish("topic/cpu_reply/messages", row[1])
        print(row[1])

def get_last_10_records_from_table2(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM projects2 ORDER BY Sensor_ID DESC LIMIT 10")

    rows = cur.fetchall()

    print("********************** L A S T 10 RECORDS ***************************")
    for row in rows:
        client.publish("topic/mem_reply/messages", row[1])
        print(row[1])



def on_message(client, userdata, message):
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)
    real_msg = str(message.payload.decode("utf-8"))
    real_topic = str(message.topic.decode("utf-8"))
    print("888888888888888888888888888888888888")
    print("Topic: " + real_topic)
    print("Message: " + real_msg)
    print("888888888888888888888888888888888888")

    if real_topic == "topic/cpu_request/messages":
        print("Request for CPU received")
        print(str(message.topic))
        publish_mqtt()

    if real_topic == "topic/mem_request/messages":
        print("Request for Memory received")
        print(str(message.topic))
        publish_mqtt2()

    else:
        print("No handler for that")
        print("Topic :" + str(message.topic))

    real_msg = ""
    real_topic = ""

def publish_mqtt():
    get_last_10_records(my_conn)

def publish_mqtt2():
    get_last_10_records_from_table2(my_conn)


def subscribe_to_mqtt():
    print("Subscribing to topic", "topic/cpu_request/messages")
    print("Subscribing to topic", "topic/mem_request/messages")
    client.subscribe([("topic/cpu_request/messages",0),("topic/mem_request/messages",0)])

class UDPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        global count
        global host_part
        global number_part

        data = self.request[0].strip()
        socket = self.request[1]

        if count == 1:
            host_part = data
            count = count + 1
        elif count == 2:
            number_part = data
            print("Host: " + str(host_part))
            print("Number: " + str(number_part))
            count = 1

            entry = (str(number_part),)

            if ("Client 1" in str(host_part)):
                if float(entry[0]) > 30:
                    create_project(my_conn, entry)

                    print("Saved Entry: " + entry[0])
            elif ("Client 2" in str(host_part)):
                if float(entry[0]) > 40:
                    create_project2(my_conn, entry)

        current_thread = threading.current_thread()
        print("{}: client: {}, wrote: {}".format(current_thread.name, self.client_address, data))
        socket.sendto(data.upper(), self.client_address)



class UDPServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
    pass

if __name__ == "__main__":

    create_connection("testdb.db")

    test_sql = """ CREATE TABLE IF NOT EXISTS projects(
            id integer PRIMARY KEY,
            Sensor_ID integer NOT NULL

        ); """

    my_conn = sqlite3.connect("testdb.db", check_same_thread=False)
    create_table(my_conn, test_sql)


    test_sql2 = """ CREATE TABLE IF NOT EXISTS projects2(
            id integer PRIMARY KEY,
            Sensor_ID integer NOT NULL

        ); """

    create_table(my_conn, test_sql2)



    HOST, PORT = "0.0.0.0", 8888

    server = UDPServer((HOST, PORT), UDPRequestHandler)

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True


    broker_address = "broker.hivemq.com"
    print("creating new instance")
    client = mqtt.Client("P1")  # create new instance
    client.on_message = on_message  # attach function to callback
    print("connecting to broker")
    client.connect(broker_address)  # connect to broker


    subscribe_to_mqtt()
    client.loop_start()  # start the loop
    try:
        server_thread.start()
        print("Server started at {} port {}".format(HOST, PORT))
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        server.shutdown()
        server.server_close()
        client.loop_stop()
        print("******* Print All Data 1     **********")
        select_all_projects(my_conn)
        print("******* Print All Data 2     **********")
        select_all_projects2(my_conn)

        get_last_10_records(my_conn)
        print("**************************************")
        get_last_10_records_from_table2(my_conn)

        exit()
