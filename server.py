import threading
import socket

PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = {}  # Dictionary to map client names to their connections
clients_lock = threading.Lock()

def handle_client(conn, addr):
    """Handles individual client connections."""
    print(f"[NEW CONNECTION] {addr} Connected")

    try:
        client_name = conn.recv(1024).decode(FORMAT)  # First message is client's name
        print(f"Client name: {client_name}")

        with clients_lock:
            clients[client_name] = conn  # Register the client in the dictionary

        connected = True
        while connected:
            msg = conn.recv(1024).decode(FORMAT)
            if not msg:
                break

            if msg == DISCONNECT_MESSAGE:
                connected = False

            if ":" in msg:  # Direct client-to-client message format: "target_client:message"
                target_client, actual_msg = msg.split(":", 1)
                with clients_lock:
                    if target_client in clients:
                        clients[target_client].sendall(f"[{client_name}] {actual_msg}".encode(FORMAT))
                        # Send acknowledgment back to the sender
                        conn.sendall(f"Message to {target_client} received.".encode(FORMAT))
                    else:
                        conn.send(f"{target_client} not found".encode(FORMAT))
            else:
                # Broadcast message to all clients (if not a direct message)
                with clients_lock:
                    for c in clients.values():
                        c.sendall(f"[{client_name}] {msg}".encode(FORMAT))
                # Send acknowledgment back to the sender
                conn.sendall("Broadcast message received.".encode(FORMAT))

    finally:
        with clients_lock:
            if client_name in clients:
                del clients[client_name]  # Remove client on disconnect

        conn.close()
        print(f"[DISCONNECTED] {addr} disconnected.")

def start():
    print('[SERVER STARTED]! Waiting for connections...')
    server.listen()
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

start()
