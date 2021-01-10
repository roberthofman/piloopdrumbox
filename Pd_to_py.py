import socket
from main import socket_message

PORT_RECV_FROM_PD = 4000
ADDRESS = "127.0.0.1"

def handle_status(action, payload):
    if action == "clear_rec":
        print("Received: " + action + ": " + str(payload))
    elif action == "start_rec":
        print("Received: " + action + ": " + str(payload))
    elif action == "stop_rec":
        print("Received: " + action + ": " + str(payload))
    elif action == "wait_rec":
        print("Received: " + action + ": " + str(payload))
    elif action == "mute_rec":
        print("Received: " + action + ": " + str(payload))
    else:
        print("unknown status received from PD")
    socket_message = {action: payload}

def setMetronome(count):
    metronome = count

def pd_receive(address, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Avoid bind() exception: OSError: [Errno 48] Address already in use
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind((address, port))
        s.listen(5) #queue messages
    except Exception as e:
        print("Socket setup failed: \n" + str(e))
    while True:
        conn, addr = s.accept()
        print("PD connected")
        for line in conn.makefile():
            yield line
        conn.close()
    s.close()

for message in pd_receive(ADDRESS, PORT_RECV_FROM_PD):
    #print("got message: ", message)
    x = message.split("|") #x[0] has the route, x[1] the value
    x.pop() #remove last element of the list (PD automatically adds \n)
    if x[0] == "counter":
        setMetronome(x[1])
    if x[0] == "status":
        handle_status(x[1], x[2:])
