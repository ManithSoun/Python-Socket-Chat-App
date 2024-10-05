import socket
import threading
import time
from datetime import datetime

PORT = 5051
SERVER = "127.0.0.1"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
RECONNECT_DELAY = 5  # Seconds before retrying to connect

def get_current_time():
    """Returns the current time formatted as a string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def connect():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(ADDR)
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return None
    return client

def send(client, msg):
    try:
        message = msg.encode(FORMAT)
        client.sendall(message)
    except Exception as e:
        print(f"[ERROR] Failed to send message: {e}")

def receive(client):
    while True:
        try:
            message = client.recv(1024).decode(FORMAT)
            if message:
                print(f"\r\033[1;32m{message}\n\033[1;37m{username}: \033[0m", end="", flush=True)  # Green for received messages
        except Exception as e:
            print(f"[ERROR] {e}")
            break

def reconnect():
    """Attempts to reconnect the client if disconnected."""
    while True:
        print(f"\033[1;33mReconnecting in {RECONNECT_DELAY} seconds...\033[0m")  # Yellow for reconnecting message
        time.sleep(RECONNECT_DELAY)
        connection = connect()
        if connection:
            send(connection, username)
            return connection

def start():
    global username
    username = input('\033[1;36mEnter your username: \033[0m')  # Cyan for username input
    answer = input(f'\033[1;36mConnect as {username}? (yes/no): \033[0m')
    if answer.lower() != 'yes':
        return

    connection = connect()
    if not connection:
        connection = reconnect()

    send(connection, username)

    # Start a thread to handle incoming messages
    receive_thread = threading.Thread(target=receive, args=(connection,))
    receive_thread.daemon = True
    receive_thread.start()

    while True:
        msg = input(f"\033[1;37m{username}: \033[0m")  # White for user input

        if msg.lower() == 'q':
            send(connection, DISCONNECT_MESSAGE)
            break

        if msg.startswith("@"):
            # Private message to a specific user
            send(connection, msg)
        else:
            send(connection, msg)

    print('\033[1;31mDisconnected\033[0m')  # Red for disconnected message
    connection.close()

start()
