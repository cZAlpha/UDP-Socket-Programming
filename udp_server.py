import socket
import os
import hashlib  # needed to verify file hash


IP = '127.0.0.1'  # change to the IP address of the server
PORT = 12000  # change to a desired port number
BUFFER_SIZE = 1024  # change to a desired buffer size


def get_file_info(data: bytes): #  -> (str, int) # Had to remove this, this was throwing an error
    file_name = data[8:].decode()
    file_size = int.from_bytes(data[:8],byteorder='big')
    return file_name, file_size


def upload_file(server_socket: socket, file_name: str, file_size: int):
    print("[+] upload_file function has commenced...")
    
    # create a SHA256 object to verify file hash
    # TODO: section 1 step 5 in README.md file
    sha256 = hashlib.sha256(file_name.encode())
    
    # create a new file to store the received data
    with open(file_name+'.temp', 'wb') as file:
        # TODO: section 1 step 7a - 7e in README.md file
        
        # 7a
        counter = 0
        received_file_size = 0
        
        while received_file_size < file_size: # 7e  
            chunk, client_address = server_socket.recvfrom(BUFFER_SIZE) # Receive a chunk of data
            
            # 7b
            file.write(chunk) # Write the data to the file
            
            # 7c
            sha256.update(chunk) # Update hash
            
            # 7d
            server_socket.sendto(b'received', client_address) # Send received message to client
            
            print(f"[+] Chunk {counter} has been received")
            counter += 1 # Increment loop var
            received_file_size += len(chunk)
    
    print("[+] All chunks have been received.")
    
    # get hash from client to verify
    # TODO: section 1 step 8 in README.md file
    client_hash, client_address = server_socket.recvfrom(BUFFER_SIZE)
    
    # TODO: section 1 step 9 in README.md file
    if (client_hash == sha256.digest()):
        print("[+] File tranfser was successful.")
        server_socket.sendto(b'success', client_address)
    else:
        print("[+] File tranfser FAILED. Hashes did not match")
        server_socket.sendto(b'failed', client_address)
    
    print("[+] upload_file function has concluded.")


def start_server():
    # create a UDP socket and bind it to the specified IP and port
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((IP, PORT))
    print(f'Server ready and listening on {IP}:{PORT}')
    
    try:
        while True:
            # TODO: section 1 step 2 in README.md file
            data, client_address = server_socket.recvfrom(BUFFER_SIZE)
            print(f"[+] Client has sent data: {data}")
            
            # expecting an 8-byte byte string for file size followed by file name
            # TODO: section 1 step 3 in README.md file
            file_name, file_size = get_file_info(data)
            
            # TODO: section 1 step 4 in README.md file
            server_socket.sendto(b'go ahead', client_address) 
            print("[+] Sending 'go ahead' to Client.")
            
            # Upload file function call
            upload_file(server_socket, file_name, file_size)
            
    except KeyboardInterrupt as ki:
        print(f"A keyboard interrupt has occurred. Was: {ki}")
    except Exception as e:
        print(f'An error occurred while receiving the file: {e}')
    finally:
        server_socket.close()
    
    print("[+] Server shutting down...")


if __name__ == '__main__':
    start_server()
