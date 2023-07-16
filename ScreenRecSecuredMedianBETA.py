import socket
import threading
import subprocess
import cv2
import pyautogui
import numpy as np
import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import time

# Define the IP address and port for the remote server
REMOTE_SERVER_IP = 'SERVER IP ADDREESS' #MAKE SURE TO CHANGE THIS for your Remote SERVER IP address!!!!!
REMOTE_SERVER_PORT = 5678 #MAKE SURE TO Change this to port to your desired and forwarded port on Remote server where local server will try to connect

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
    output_file = f"output_{datetime_str}_{counter}.avi"

    # Define the codec for video encoding
    fourcc = cv2.VideoWriter_fourcc(*"XVID")

    # Get the screen size
    screen_size = pyautogui.size()

    # Create the video writer object
    video_writer = cv2.VideoWriter(output_file, fourcc, 30.0, screen_size, isColor=True)

    # Start recording the screen
    start_time = cv2.getTickCount()

    # Send a notification that the recording has started
    print(f"Screen recording {counter} started.")

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

        # Convert PIL image to OpenCV format
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

        elif command == 'STOP':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

            self.wfile.write(b'Screen recording stopped!')

        else:
            self.send_response(401)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

            self.wfile.write(b'Unauthorized command!')

# Function to start the local server
def start_local_server():
    server_address = ('', 4000)  # Listen on all available interfaces
    httpd = HTTPServer(server_address, CommandHandler)
    print(f'Local server listening on port 4000')
    httpd.serve_forever()

# Function to establish a connection with the remote server and send commands
# Function to establish a connection with the remote server and send commands
# Function to establish a connection with the remote server and send commands
def establish_connection_with_remote():
    while True:
        try:
            # Establish a connection with the remote server
            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_socket.connect((REMOTE_SERVER_IP, REMOTE_SERVER_PORT))

            while True:
                # Wait for commands from the remote server
                command = remote_socket.recv(1024).decode()

                # Process the command
                if command == 'START':
                    # Start screen recording
                    record_screen(RECORDING_DURATION, recording_counter)
                    response = 'Screen recording started!'

                elif command == 'STOP':
                    # Stop screen recording
                    response = 'Screen recording stopped!'

                else:
                    # Invalid command or idle state, do nothing
                    response = ''

                # Send the response back to the remote server
                remote_socket.sendall(response.encode())

        except Exception as e:
            print(f'Error establishing connection with remote server: {str(e)}')
            # Retry after a certain interval if the connection is lost
            time.sleep(5)


        except Exception as e:
            print(f'Error establishing connection with remote server: {str(e)}')
            # Retry after a certain interval if the connection is lost
            time.sleep(5)


# Start the local server in a separate thread
local_server_thread = threading.Thread(target=start_local_server)
local_server_thread.start()

# Start establishing connection with the remote server
establish_connection_thread = threading.Thread(target=establish_connection_with_remote)
establish_connection_thread.start()

# Wait for the local server thread to finish
local_server_thread.join()
