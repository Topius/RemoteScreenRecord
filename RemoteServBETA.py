import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Define the IP address and ports for the servers
REMOTE_SERVER_IP = 'LOCAL IP ADDRESS' #MAKE SURE TO CHANGE THIS for your Machine IP address!!!!!
REMOTE_SERVER_PORT = 1234 #On this Port HTML file will send Request
LOCAL_SERVER_PORT = 5678  #On this Port Local Server will try to connect.

# Array to store connected HTML clients
html_clients = []

# Function to handle the commands received from the local server
def handle_command(command):
    # Perform actions based on the command
    if command == 'START':
        # Start the desired process or perform any other actions
        print('Received START command')
        return forward_command_to_local_server(command)

    elif command == 'STOP':
        # Stop the desired process or perform any other actions
        print('Received STOP command')
        return forward_command_to_local_server(command)

    else:
        is_idle = True
        return 'Invalid command!'

# Function to forward the command to the local server
def forward_command_to_local_server(command):
    # Create a socket and connect to the local server
    local_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    local_server_socket.connect(('localhost', LOCAL_SERVER_PORT))

    try:
        # Send the command to the local server
        local_server_socket.sendall(command.encode())

        # Receive the response from the local server
        response = local_server_socket.recv(1024).decode()
        return response

    finally:
        # Close the socket connection to the local server
        local_server_socket.close()

# Function to handle connections from the HTML clients
def handle_html_clients(client_socket):
    while True:
        try:
            # Receive the command from the HTML client
            command = client_socket.recv(1024).decode()

            if not command:
                break

            print(f'Command received from HTML client: {command}')

            # Handle the received command
            response = handle_command(command)

            # Send the response back to the HTML client
            client_socket.sendall(response.encode())

        except Exception as e:
            print(f'Error handling HTML client message: {str(e)}')
            break

    # Remove the client socket from the connected HTML clients array
    html_clients.remove(client_socket)
    client_socket.close()

# HTTP request handler class for receiving commands from the HTML clients
class CommandHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        command = self.rfile.read(content_length).decode('utf-8')

        if command:
            # Forward the command to the connected HTML clients
            for client_socket in html_clients:
                client_socket.sendall(command.encode())

            self.send_response(200)
        else:
            self.send_response(400)

        self.end_headers()

# Function to establish a reverse connection from the local server to the remote server
def establish_reverse_connection():
    # Create a socket and bind it to any available port on the local server
    local_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    local_server_socket.bind(('0.0.0.0', LOCAL_SERVER_PORT))
    local_server_socket.listen(1)
    print('Reverse connection listening for local server...')

    while True:
        # Accept a connection from the local server
        client_socket, client_address = local_server_socket.accept()
        print(f'Local server connected: {client_address}')

        # Add the client socket to the connected HTML clients array
        html_clients.append(client_socket)

        # Start a new thread to handle messages from the HTML client
        threading.Thread(target=handle_html_clients, args=(client_socket,)).start()

# Function to start the remote server
def start_remote_server():
    server_address = (REMOTE_SERVER_IP, REMOTE_SERVER_PORT)
    httpd = HTTPServer(server_address, CommandHandler)
    print(f'Remote server listening on {REMOTE_SERVER_IP}:{REMOTE_SERVER_PORT}')
    httpd.serve_forever()

# Start the reverse connection from the local server to the remote server
reverse_connection_thread = threading.Thread(target=establish_reverse_connection)
reverse_connection_thread.start()

# Start the remote server
start_remote_server()
