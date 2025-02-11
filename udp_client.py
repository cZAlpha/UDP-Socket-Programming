import socket
import hashlib  # needed to calculate the SHA256 hash of the file
import sys  # needed to get cmd line parameters
import os.path as path  # needed to get size of file in bytes
import math


DR_R_SERVER_IP = '10.33.20.21'
#IP = DR_R_SERVER_IP
IP = '127.0.0.1'  # change to the IP address of the server
PORT = 12000  # change to a desired port number
BUFFER_SIZE = 1024  # change to a desired buffer size

FILE_PATH = "/Users/nbklaus21/Documents/VSCodeProjects/devDSU2025/ComputerNetworking/ProgrammingAssignments/ProgrammingAssignment1/UDP-Socket-Programming/vs_code.png"
FILE_PATH_TXT = "/Users/nbklaus21/Documents/VSCodeProjects/devDSU2025/ComputerNetworking/ProgrammingAssignments/ProgrammingAssignment1/UDP-Socket-Programming/text_file.txt"

def get_file_size(file_name: str) -> int:
    size = 0
    try:
        size = path.getsize(file_name)
    except FileNotFoundError as fnfe:
        print(fnfe)
        sys.exit(1)
    return size


def send_file(filename: str):
    print("[+] send_file function has commenced...")
    # get the file size in bytes
    # TODO: section 2 step 2 in README.md file
    file_size = get_file_size(filename)
    
    # convert the file size to an 8-byte byte string using big endian
    # TODO: section 2 step 3 in README.md file
    file_size = file_size.to_bytes(8, "big")
    
    # create a SHA256 object to generate hash of file
    # TODO: section 2 step 4 in README.md file
    sha256 = hashlib.sha256(file_name.encode())
    
    # create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("[+] Client socket has been created.")
    
    try:
        # send the file size in the first 8-bytes followed by the bytes
        # for the file name to server at (IP, PORT)
        # TODO: section 2 step 6 in README.md file
        data = file_size + file_name.encode() # File size (big endian) concatonated with the file name
        client_socket.sendto(data, (IP, PORT)) # Send that data
        print(f"[+] Data sent to server: {data}", "| Size: ", get_file_size(filename))
        
        # TODO: section 2 step 7 in README.md file
        response, address = client_socket.recvfrom(BUFFER_SIZE)
        print("Response: ", response, " Address: ", address)

        if response != b'go ahead':
            raise Exception('Bad server response - was not go ahead!')
        print("[+] Received 'go ahead' from server.")
        
        num_of_chunks = math.ceil(get_file_size(file_name) / BUFFER_SIZE)
        print(f"[+] {num_of_chunks} chunks to send.")
        
        print("[+] Starting file transfer...")
        # open the file to be transferred
        
        with open(file_name, 'rb') as file: 
            # TODO: section 2 step 8 a-d in README.md file | read the file in chunks and send each chunk to the server
            # 8a
            chunk = file.read(BUFFER_SIZE)
            
            counter = 0
            # 8b
            while chunk:
                print(f"[+] Sending chunk #{counter}")
                counter += 1
                sha256.update(chunk) # 8b-i
                client_socket.sendto(chunk, address) # 8b-ii
                response = client_socket.recv(BUFFER_SIZE)
                if response != b'received': # 8b-iii
                    raise Exception("Bad server response - was not received!")
                chunk = file.read(BUFFER_SIZE)
        
        # send the hash value so server can verify that the file was
        # received correctly.
        # TODO: section 2 step 9 in README.md file
        client_socket.sendto(sha256.digest(), address)
        
        # TODO: section 2 steps 10 in README.md file
        response = client_socket.recv(BUFFER_SIZE)
        
        # TODO: section 2 step 11 in README.md file
        if response == b'failed':
            raise Exception('Transfer failed!')
        elif response == b'success':
            print('[+] Transfer completed successfully!')
        else:
            raise Exception('Transfer INCOMPLETE. No response from server after file transfer finished.')
        
    except Exception as e:
        print(f'An error occurred while sending the file: {e}')
    finally:
        client_socket.close()
    print("[+] send_file function has concluded.")


if __name__ == "__main__":
    # get filename from cmd line
    if len(sys.argv) < 2:
        print(f'SYNOPSIS: {sys.argv[0]} <filename>')
        sys.exit(1)
    file_name = sys.argv[1]  # filename from cmdline argument
    send_file(file_name)
