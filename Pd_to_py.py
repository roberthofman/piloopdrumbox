import socket

PORT_RECV_FROM_PD = 4000
ADDRESS = "127.0.0.1"

def setMetronome(count):
    metronome = count
    print(metronome)

def pdreceive(address, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Avoid bind() exception: OSError: [Errno 48] Address already in use
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind((address, port))
        s.listen(5) #queue messages
    except s.error as e:
        print("socket setup failed:" + str(e))

    while True:
        conn, addr = s.accept()
        print("PD connected")
        for line in conn.makefile():
            yield line
        conn.close()
    s.close()

for message in pdreceive(ADDRESS, PORT_RECV_FROM_PD):
    #print("got message: ", message)
    x = message.split("|") #x[0] has the route, x[1] the value
    if x[0] == "counter":
        setMetronome(x[1])
