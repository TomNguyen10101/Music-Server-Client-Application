from ClientModel import Playlist, Song
import random
import pygame
import socket
from io import BytesIO
from tkinter import END
from credentials import *

class MusicController:
    def __init__(self, **kwargs):
        # Volume Variable(s)
        self.mute = False
        self.preVol = 0.0

        # Initiate Playlist object
        self.playlist = Playlist()

        # Instantiate a Pygame (music mixer) object
        pygame.init()
        pygame.mixer.init()
        self.songEnd = False
        self.SONG_END = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.SONG_END)
        self.preVol = pygame.mixer.music.get_volume()

        # Some GUI variables for easy adjustment
        argsDict = dict(kwargs.items())
        self.root = argsDict["root"]
        self.trackTextBox = argsDict['trackTextBox']
        self.playBtn = argsDict['playBtn']
        self.playImage = argsDict['playImg']
        self.pauseImage = argsDict["pauseImg"]
        self.track = argsDict["track"]
        self.onlBtn = argsDict["onlBtn"]
        self.searchBox = argsDict["searchBox"]
        self.searchBtn = argsDict["searchBtn"]
        self.enableClr = "#CD4F39"
        self.disableClr = "#808080"

        # Track State Variable(s)
        self.singleLoop = False
        self.loop = False
        self.shuffle = False
        self.pause = False
        self.isRunning = False
        self.stop = True
        self.loopState = 0

        self.prevIndex = None
        self.currIndex = None

        # Connection Flag && Variables
        self.isConnected = False
        self.clientToServerSocket = None

    # Play the current song
    def Play(self):
        if(self.pause == False and self.isRunning == True):
            self.playBtn.configure(image=self.playImage)
            self.Pause()
        else:
            self.playBtn.configure(image=self.pauseImage)
            pygame.mixer.music.unpause()
            self.pause = False

        # Case: Play the list when first started without current song
        if(self.playlist.currentSong == None):
            if(self.shuffle == True):
                self.Shuffle()
            else:
                self.playlist.currentSong = self.playlist.head
                self.currIndex = 0

        if(not self.isRunning):
            try:
                if not self.playlist.currentSong.offline:
                    fileToPlay = BytesIO(self.playlist.currentSong.file)
                else:
                    fileToPlay = self.playlist.currentSong.file

                pygame.mixer.music.load(fileToPlay)
                pygame.mixer.music.play()

                # Hard To Do: Add a fade effect between songs

                self.track.set(self.playlist.currentSong.name)

                if(self.prevIndex is None):
                    self.trackTextBox.itemconfig(self.currIndex, {'fg': self.enableClr})
                else:
                    self.trackTextBox.itemconfig(self.prevIndex, {'fg': '#fff'})
                    self.trackTextBox.itemconfig(self.currIndex, {'fg': self.enableClr})
                
                self.isRunning = True
                self.stop = False

            except Exception as e:
                print(f"Can't Play Audio.Error: {str(e)}")

    # This method is for checking whether the song has ended 
    # --> To move to the next song depends on the option of the user     
    def CheckSongStatus(self, root):
        for event in pygame.event.get():
            if event.type == self.SONG_END:
                self.isRunning = False
                if(not self.stop):
                    if self.singleLoop:
                        self.Play()
                    elif self.shuffle:
                        self.Shuffle()
                        self.Play()
                    elif(self.playlist.currentSong.next is not None and not self.singleLoop):
                        self.playlist.currentSong = self.playlist.currentSong.next
                        self.Play()
                    elif self.loop:
                        self.playlist.currentSong = self.playlist.head
                        self.prevIndex = self.currIndex
                        self.currIndex = 0
                        self.Play()
                    else:
                        pygame.mixer.music.stop()
                        self.stop = True
                break
        
        # root will run this method after every 100 millisecs
        root.after(100, self.CheckSongStatus, root)

    # Pause the current song
    def Pause(self):
        pygame.mixer.music.pause()
        self.pause = True

    # Skip the current song
    def Forward(self):
        self.isRunning = False
        if self.playlist.currentSong is None:
            return
        if(self.playlist.currentSong.next is not None):
            self.playlist.currentSong = self.playlist.currentSong.next
            if self.currIndex < (self.playlist.size - 1):
                self.prevIndex = self.currIndex    
                self.currIndex += 1
            self.Play()
        else:
            pygame.mixer.music.stop()
            self.stop = True

    # Play the previous song
    def Backward(self):
        self.isRunning = False
        if self.playlist.currentSong is None:
            return
        if(self.playlist.currentSong.prev is not None):
            self.playlist.currentSong = self.playlist.currentSong.prev
            if self.currIndex > 0:
                self.prevIndex = self.currIndex    
                self.currIndex -= 1
            self.Play()
        else:
            pygame.mixer.music.stop()
            self.stop = True
    
    # Shuffle the playlist --> assign the next song to play 
    def Shuffle(self):
        randomIndex = random.randint(0, self.playlist.size - 1)
        self.playlist.Get(randomIndex) 

        if(self.prevIndex is None):
            self.currIndex = randomIndex
        else:
            self.prevIndex = self.currIndex
            self.currIndex = randomIndex        

    # Stop the current song
    def Stop(self):
        pygame.mixer.music.stop()
        self.stop = True

    # Adjust Volumn using the value get from the slider
    def AdjustVolume(self, value):
        self.preVol = value * 0.01
        pygame.mixer.music.set_volume(self.preVol)     


    ####### PLAYLIST CODE SECTION ########
    # Get playlist size 
    def GetPlaylistSize(self):
        return self.playlist.size
    
    # Get a song with a specific index in the playlist
    def GetIndex(self, index):
        return self.playlist.Get(index)
    
    # Get the current song
    def GetCurrentSong(self):
        return self.playlist.currentSong
    
    # Get song list
    def GetSongList(self):
        return self.playlist.songlist

    # Remove a specific song from the playlist 
    def RemoveFromPlayList(self, file):
        return self.playlist.Remove(file)
    
    # Add a song to the playlist
    def AddToPlaylist(self, newSong):
        return self.playlist.Append(newSong)
    
    # Clear the playlist (memory efficient)
    def ClearPlaylist(self):
        self.playlist.Clear()
    
    #######################################

    ####### NETWORKING CODE SECTION #######
    # finally:
    #     # with open("my_file.mp3", "wb") as binary_file:
    #     #     # Write bytes to file
    #     #     binary_file.write(buffer)
    #     pass

    def ConnectToServer(self):
        buffer = b''
        self.onlBtn.configure(state="disable", fg_color= self.disableClr)
        try:
                self.clientToServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.clientToServerSocket.connect((HOST_IP, HOST_PORT))
                self.onlBtn.configure(state="normal",text="Go Offline", fg_color=self.enableClr)
                self.searchBox.configure(state="normal")
                self.searchBtn.configure(state="normal", fg_color=self.enableClr)
                self.isConnected = True

                #Start listening after successfully connected to the server
                while self.isConnected:
                    data = self.clientToServerSocket.recv(1024)
                    buffer += data
                    if b'__END_OF_TRANSMISSION__' in data:
                        print("End of transmission received.")
                        self.HandleServerMsg(buffer)
                        buffer = b''
                
                return True

        except socket.error as error:
                print(f"{error}")
                return False
        
    def SearchSong(self,query):
            if self.isConnected:
                self.clientToServerSocket.sendall(bytes(f'Search:{query}', 'utf-8'))
            else:
                print("Not connected to the server")

    def HandleServerMsg(self,buffer):
        if b'No Result' in buffer:
            print("No Result")
        else:
            songInfo = buffer.split(b'__NEXT_HEADER__')
            songName = songInfo[0].split(b'__NAME__')[1]
            songStream = songInfo[1].split(b'__FILE__')[1]
            try:
                newSong = Song(file=songStream, name=songName.decode('utf-8'),offline=False)
                try:
                    self.AddToPlaylist(newSong)
                    self.trackTextBox.configure(state="normal")
                    self.trackTextBox.insert(END, f"{self.GetPlaylistSize()}. {newSong.name}")
                except Exception as e:
                    print(e)

            except Exception as e:
                print(f"Error playing audio. Error: {e}")
                
        self.searchBox.configure(state="normal")
        self.searchBtn.configure(state="normal", fg_color=self.enableClr)
      
    def GoOffline(self):
        self.isConnected = False







    

     