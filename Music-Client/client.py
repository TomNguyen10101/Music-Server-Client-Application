import socket
import pygame
from io import BytesIO
HOST = 'localhost'
PORT = 8000

buffer = b''
pygame.init()
pygame.mixer.init()
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'Hello World!')

    while True:
        data = s.recv(1024)
        buffer += data
        if b'__END_OF_TRANSMISSION__' in data:
                print("End of transmission received.")
                break
        
        
# Play the music buffer
try:
    sound = pygame.mixer.Sound(BytesIO(buffer))
    sound.play()
    pygame.time.wait(int(sound.get_length() * 1000))  # Wait for the sound to finish playing
    
except pygame.error as e:
    print(f"Error playing audio: {e}")
finally:
    # with open("my_file.mp3", "wb") as binary_file:
    #     # Write bytes to file
    #     binary_file.write(buffer)
    pass