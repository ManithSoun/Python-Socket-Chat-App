import threading
import socket
from datetime import datetime

PORT = 5051
SERVER = "127.0.0.1"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = {}
clients_lock = threading.Lock()

def get_current_time():
    """Returns the current time formatted as a string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def handle_client(conn, addr):
    try:
        # Receive username
        username = conn.recv(1024).decode(FORMAT)
        print(f"\r\033[1;34m[{get_current_time()}] [NEW CONNECTION]\033[0m {addr} with username: \033[1;32m{username}\033[0m connected.\n\033[1;35m[Server Message]:\033[0m ", end="", flush=True)
        
        with clients_lock:
            clients[conn] = username
        
        # Notify others that a new user has joined
        join_message = f"\033[3;34m{username} joined the room\033[0m"  # Blue join message
        broadcast_message(join_message, conn)

        connected = True
        while connected:
            msg = conn.recv(1024).decode(FORMAT)
            if not msg:
                break

            if msg == DISCONNECT_MESSAGE:
                connected = False
                disconnect_message = f"\033[3;31m{username} has left the chat.\033[0m"  # Red disconnect message
                print(disconnect_message)
                broadcast_message(disconnect_message, conn)
            else:
                # Display client message
                formatted_message = f"[{get_current_time()}] {username}: {msg}             "
                print(f"\r\033[1;33m{formatted_message}\033[0m\n\033[1;35m[Server Message]:\033[0m ", end="", flush=True)  # Yellow for client message
                broadcast_message(formatted_message, conn)

    finally:
        with clients_lock:
            del clients[conn]
        conn.close()

def broadcast_message(message, sender_conn=None):
    """Broadcasts a message to all connected clients except the sender."""
    with clients_lock:
        for c in clients:
            if c != sender_conn:  # Avoid sending the message back to the sender
                try:
                    c.sendall(message.encode(FORMAT))
                except Exception as e:
                    print(f"[ERROR] Failed to send message to {clients[c]}: {e}")

def server_input():
    while True:
        message = input("\033[1;36m[Server Message]:\033[0m ")  # Cyan text for server messages
        if message:  # Ensure the message is not empty
            broadcast_message(f"\033[1;36m[Server]: {message}        \033[0m")  # Broadcast server message to all clients

def start():
    print('\033[1;32m[SERVER STARTED]!\033[0m')  # Green for server start
    server.listen()

    # Start a thread for server input so that the server can send messages while handling clients
    threading.Thread(target=server_input, daemon=True).start()

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

start()
