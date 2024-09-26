import socket
import threading

PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

def receive_messages(client_socket):
    """Continuously listen for incoming messages."""
    while True:
        try:
            msg = client_socket.recv(1024).decode(FORMAT)
            if not msg:
                break
            print(f"\n[Message Received] {msg}")
        except:
            print("[ERROR] Connection lost.")
            break

def connect_to_server():
    """Connect to the server."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(ADDR)
        print("Connected to server.")
    except Exception as e:
        print(f"[ERROR] {e}")
        return None
    return client

def send_to_server(client, msg):
    message = msg.encode(FORMAT)
    client.send(message)

def client_to_client(selected_client, target_client, client_socket):
    """Handles client-to-client communication."""
    print(f"\n[Client {selected_client}] Chatting with {target_client}...")

    threading.Thread(target=receive_messages, args=(client_socket,)).start()

    while True:
        msg = input(f"Message to {target_client} (q to quit): ")
        if msg.lower() == 'q':
            break

        # Send message to target client via the server
        full_msg = f"{target_client}:{msg}"
        send_to_server(client_socket, full_msg)

    # Ask what to do next
    next_action(client_socket, selected_client)

def next_action(client_socket, selected_client):
    while True:
        action = input("Do you want to continue chatting with another client, the server, or quit? (c/s/q): ").lower()
        if action == 'c':
            target_client = input(f"Which client would you like to chat with? ({', '.join(clients)}): ")
            if target_client in clients:
                client_to_client(selected_client, target_client, client_socket)
            else:
                print("[ERROR] Invalid client selection. Please try again.")
        elif action == 's':
            chat_with_server(client_socket, selected_client)  # Pass selected_client here
        elif action == 'q':
            send_to_server(client_socket, DISCONNECT_MESSAGE)
            print("Disconnected from the server.")
            break
        else:
            print("[ERROR] Invalid selection. Please choose 'c' for client, 's' for server, or 'q' to quit.")

def chat_with_server(client_socket, selected_client):
    while True:
        msg = input("Enter a message for the server (q to quit): ")
        if msg.lower() == 'q':
            send_to_server(client_socket, DISCONNECT_MESSAGE)
            print("Disconnected from the server.")
            break
        send_to_server(client_socket, msg)
        print("[Message Sent] Server acknowledged your message.")

    next_action(client_socket, selected_client)

def start():
    create_clients = int(input("How many clients would you like to create? "))
    global clients
    clients = [f"Client {i+1}" for i in range(create_clients)]
    print(f"\nClients created: {', '.join(clients)}")

    while True:
        connection_type = input("Do you want to connect with the server or a client? (s/c): ").lower()

        if connection_type == "s":
            connection = connect_to_server()
            if connection is None:
                return
            chat_with_server(connection, "Server")

        elif connection_type == "c":
            connection = connect_to_server()
            if connection is None:
                return

            selected_client = input("Enter your client name: ")
            send_to_server(connection, selected_client)

            target_client = input(f"Which client would you like to chat with? ({', '.join(clients)}): ")
            if target_client in clients:
                client_to_client(selected_client, target_client, connection)
            else:
                print("[ERROR] Invalid client selection. Please try again.")
        else:
            print("[ERROR] Invalid selection. Please choose 's' for server or 'c' for client.")

start()
