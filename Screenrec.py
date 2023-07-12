import socket
import threading
import subprocess
import cv2
import pyautogui
import numpy as np
import datetime

# Define the IP address and ports for starting and stopping recording
IP_ADDRESS = '192.168.100.97'
START_PORT = 1234
STOP_PORT = 5678

# Define the screen recording duration in seconds
RECORDING_DURATION = 10

# Counter to keep track of the recordings
recording_counter = 1

# Function to handle start requests
def handle_start_request(client_socket):
    global recording_counter

    print("Start request received. Starting screen recording...")

    # Create a thread to perform the screen recording
    record_thread = threading.Thread(target=record_screen, args=(RECORDING_DURATION, recording_counter))
    record_thread.start()

    # Increment the recording counter
    recording_counter += 1

    # Send a response to the client
    response = "Screen recording started!"
    client_socket.send(response.encode())

    # Close the client socket
    client_socket.close()

# Function to perform screen recording
def record_screen(duration, counter):
    # # Specify the output file name
    # output_file = f"output{counter}.mp4"

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

# Function to handle stop requests
def handle_stop_request(client_socket):
    print("Stop request received. Stopping screen recording...")

    # Send a response to the client
    response = "Screen recording stopped!"
    client_socket.send(response.encode())

    # Close the client socket
    client_socket.close()

# Function to start the server for starting requests
def start_start_server():
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the IP address and port to the socket
    server_socket.bind((IP_ADDRESS, START_PORT))

    # Listen for incoming connections
    server_socket.listen(1)
    print(f"Start server listening on {IP_ADDRESS}:{START_PORT}")

    while True:
        # Accept a client connection
        client_socket, client_address = server_socket.accept()

        # Start a new thread to handle the request
        thread = threading.Thread(target=handle_start_request, args=(client_socket,))
        thread.start()

# Function to start the server for stopping requests
def start_stop_server():
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the IP address and port to the socket
    server_socket.bind((IP_ADDRESS, STOP_PORT))

    # Listen for incoming connections
    server_socket.listen(1)
    print(f"Stop server listening on {IP_ADDRESS}:{STOP_PORT}")

    while True:
        # Accept a client connection
        client_socket, client_address = server_socket.accept()

        # Start a new thread to handle the request
        thread = threading.Thread(target=handle_stop_request, args=(client_socket,))
        thread.start()

# Start the servers in separate threads
start_server_thread = threading.Thread(target=start_start_server)
start_server_thread.start()

stop_server_thread = threading.Thread(target=start_stop_server)
stop_server_thread.start()

# Main loop
while True:
    command = input("Enter 'start' to initiate screen recording or 'stop' to stop recording: ")

    if command == 'start':
        # Send a request to the specified IP address and port for starting
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((IP_ADDRESS, START_PORT))

        # Receive the response from the server
        response = client_socket.recv(1024).decode()
        print(response)

        # Close the client socket
        client_socket.close()

    elif command == 'stop':
        # Send a request to the specified IP address and port for stopping
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((IP_ADDRESS, STOP_PORT))

        # Receive the response from the server
        response = client_socket.recv(1024).decode()
        print(response)

        # Close the client socket
        client_socket.close()

    elif command == 'quit':
        break

# Wait for the servers to finish
start_server_thread.join()
stop_server_thread.join()
