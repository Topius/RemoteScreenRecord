import socket
import threading
import subprocess
import cv2
import pyautogui
import numpy as np
import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

# Define the IP address and port for the server
IP_ADDRESS = '192.168.100.97'
COMMAND_PORT = 1234

# Define the screen recording duration in seconds
RECORDING_DURATION = 10

# Counter to keep track of the recordings
recording_counter = 1

# Function to perform screen recording
def record_screen(duration, counter):
    # Get the current date and time
    current_datetime = datetime.datetime.now()
    datetime_str = current_datetime.strftime("%Y-%m-%d_%H-%M")

    # Specify the output file name with the current date and time
    output_file = f"output_{datetime_str}_{counter}.mp4"

    # Define the codec for video encoding
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    # Get the screen size
    screen_size = (1920, 1080)  # Update with your screen size

    # Create the video writer object
    video_writer = cv2.VideoWriter(output_file, fourcc, 30.0, screen_size)

    # Start recording the screen
    start_time = cv2.getTickCount()

    while True:
        # Get the current time
        current_time = cv2.getTickCount()

        # Calculate the elapsed time
        elapsed_time = (current_time - start_time) / cv2.getTickFrequency()

        # Check if the recording duration has been reached
        if elapsed_time >= duration:
            break

        # Capture the screen frame
        frame = pyautogui.screenshot()
        frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)

        # Write the frame to the video file
        video_writer.write(frame)

    # Release the video writer
    video_writer.release()

    print(f"Screen recording {counter} completed.")

# HTTP request handler class
class CommandHandler(BaseHTTPRequestHandler):
    # Function to handle POST requests
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        command = self.rfile.read(content_length).decode('utf-8')

        if command == 'START':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

            # Increment the recording counter
            global recording_counter
            recording_counter += 1

            # Start a new thread to perform the screen recording
            record_thread = threading.Thread(target=record_screen, args=(RECORDING_DURATION, recording_counter))
            record_thread.start()

            self.wfile.write(b'Screen recording started!')
            print(f"Screen recording {recording_counter} started.")

        elif command == 'STOP':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

            self.wfile.write(b'Screen recording stopped!')
            print("Screen recording stopped.")

        else:
            self.send_response(401)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

            self.wfile.write(b'Unauthorized command!')

# Function to start the server
def start_server():
    server_address = (IP_ADDRESS, COMMAND_PORT)
    httpd = HTTPServer(server_address, CommandHandler)
    print(f'Command server listening on {IP_ADDRESS}:{COMMAND_PORT}')
    httpd.serve_forever()

# Start the server in a separate thread
server_thread = threading.Thread(target=start_server)
server_thread.start()

# Main loop
while True:
    command = input("Enter 'start' to initiate screen recording or 'stop' to stop recording: ")

    if command == 'start':
        # Send a POST request to the server for starting
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((IP_ADDRESS, COMMAND_PORT))

        request = 'POST / HTTP/1.1\r\n'
        request += f'Host: {IP_ADDRESS}:{COMMAND_PORT}\r\n'
        request += 'Content-Type: text/plain\r\n'
        request += 'Content-Length: 5\r\n\r\n'
        request += 'START'

        client_socket.sendall(request.encode())

        # Receive the response from the server
        response = client_socket.recv(1024).decode()
        print(response)

        # Close the client socket
        client_socket.close()

    elif command == 'stop':
        # Send a POST request to the server for stopping
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((IP_ADDRESS, COMMAND_PORT))

        request = 'POST / HTTP/1.1\r\n'
        request += f'Host: {IP_ADDRESS}:{COMMAND_PORT}\r\n'
        request += 'Content-Type: text/plain\r\n'
        request += 'Content-Length: 4\r\n\r\n'
        request += 'STOP'

        client_socket.sendall(request.encode())

        # Receive the response from the server
        response = client_socket.recv(1024).decode()
        print(response)

        # Close the client socket
        client_socket.close()

    elif command == 'quit':
        break

# Wait for the server to finish
server_thread.join()
