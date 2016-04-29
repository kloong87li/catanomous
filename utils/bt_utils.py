import bluetooth as bt

class BluetoothServer(object):

  _SERVER_PORT = None

  def __init__(self):
    self._server_sock = None
    return

  def start(self):
    self._server_sock = bt.BluetoothSocket(bt.RFCOMM)
    self._server_sock.bind(("", bt.PORT_ANY))
    self._server_sock.listen(1)

    port = self._server_sock.getsockname()[1]
    uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

    bt.advertise_service( self._server_sock, "CatanBTServer",
                       service_id = uuid,
                       service_classes = [ uuid, bt.SERIAL_PORT_CLASS ],
                       profiles = [ bt.SERIAL_PORT_PROFILE ]
                    )
                   
  def accept(self):
    client_sock, client_info = self._server_sock.accept()
    print "!! [BLUETOOTH] Accepted connection from ", client_info
    return client_sock

  def send(self, sock, data):
    sock.sendall(data)

  def receive(self, sock, bytes=1024):
    data = sock.recv(bytes)
    return data

  def close(self, sock):
    sock.close()

  def close_server(self):
    self._server_sock.close()


class BluetoothClient(object):

  def __init__(self):
    self._sock = None
    return

  def connect(self, addr):
    uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
    service_matches = bt.find_service( uuid = uuid , addr = addr)

    if len(service_matches) == 0:
      print("!! [BLUETOOTH] Couldn't connect.")
      return

    first_match = service_matches[0]
    port = first_match["port"]
    name = first_match["name"]
    host = first_match["host"]

    # Create the client socket
    self._sock = bt.BluetoothSocket( bt.RFCOMM )
    self._sock.connect((host, port))
    return

  def send(self, data):
    self._sock.sendall(data)
    return

  def close():
    self._sock.close()


