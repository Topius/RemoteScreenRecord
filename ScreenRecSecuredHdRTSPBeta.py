import socket
import threading
import cv2
import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import time

# Define the IP address and port for the remote server
REMOTE_SERVER_IP = 'SERVER IP ADDREESS' #MAKE SURE TO CHANGE THIS for your Remote SERVER IP address!!!!!
REMOTE_SERVER_PORT = 5678 #MAKE SURE TO Change this to port to your desired and forwarded port on Remote server where local server will try to connect

# Define the RTSP stream duration in seconds
RECORDING_DURATION = 20

# Counter to keep track of the recordings
recording_counter = 1

# Function to perform RTSP stream capture
def capture_rtsp_stream(duration, counter):
    # Get the current date and time
    current_datetime = datetime.datetime.now()
    datetime_str = current_datetime.strftime("%Y-%m-%d_%H-%M")

    # Specify the output file name with the current date and time
    output_file = f"output_{datetime_str}_{counter}.avi"

    # Define the RTSP stream URL
    rtsp_url = "TYPE RTSP STREAM URL HERE"

    # Create the capture object
    capture = cv2.VideoCapture(rtsp_url)

    # Define the codec for video encoding
    fourcc = cv2.VideoWriter_fourcc(*"XVID")

    # Get the frame rate of the RTSP stream
    fps = capture.get(cv2.CAP_PROP_FPS)

    # Get the frame size of the RTSP stream
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    screen_size = (width, height)

    # Create the video writer object
    video_writer = cv2.VideoWriter(output_file, fourcc, fps, screen_size, isColor=True)

    # Start capturing the RTSP stream
    start_time = time.time()

    # Send a notification that the RTSP stream capture has started
    print(f"RTSP stream capture {counter} started.")

    while True:
        # Check if the capture duration has been reached
        elapsed_time = time.time() - start_time
        if elapsed_time >= duration:
            break

        # Read a frame from the RTSP stream
        ret, frame = capture.read()

        # Check if the frame is valid
        if ret:
            # Write the frame to the video file
            video_writer.write(frame)

    # Release the capture and video writer objects
    capture.release()
    video_writer.release()

    print(f"RTSP stream capture {counter} completed.")

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

            # Start a new thread to perform the RTSP stream capture
            capture_thread = threading.Thread(target=capture_rtsp_stream, args=(RECORDING_DURATION, recording_counter))
            capture_thread.start()

            self.wfile.write(b'RTSP stream capture started!')

        elif command == 'STOP':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

            self.wfile.write(b'RTSP stream capture stopped!')

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
                    # Start RTSP stream capture
                    capture_rtsp_stream(RECORDING_DURATION, recording_counter)
                    response = 'RTSP stream capture started!'

                elif command == 'STOP':
                    # Stop RTSP stream capture
                    response = 'RTSP stream capture stopped!'

                else:
                    # Invalid command or idle state, do nothing
                    response = ''

                # Send the response back to the remote server
                remote_socket.sendall(response.encode())

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
