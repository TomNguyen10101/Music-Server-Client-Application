from mutagen.mp3 import MP3
import os
# A class to hold the details of the song
class Song:
    def __init__(self, file, artist=None):
        self.artist = artist
        self.file = file
        self.prev = None
        self.next = None
        self.name = os.path.basename(file).replace(".mp3","")
        
        # Get the song length
        song =  MP3(file)
        min, sec = divmod(song.info.length, 60)
        hour, min = divmod(min, 60)
        self.lengthInSec = song.info.length
        self.songLength = f"{int(min)}:{int(sec)}"

# A class that used to store all the songs
class Playlist:
    def __init__(self):
        self.head = None
        self.currentSong = None
        self.size = 0
        self.songList = []
    
    # Insert song into the playlist with specific index
    def InsertSong(self, newSong, index):
        # Traverse the list to go the suitable position to insert the node
        currentNode = self.head

        # Special case: Insert in 1st element
        if index == 0:
            if(currentNode != None):
                newSong.next = currentNode
                currentNode.prev = newSong
                self.head = newSong
            else:
                self.head = newSong  
            return

        for i in range(index - 1):
            if(currentNode.next != None):
                currentNode = currentNode.next
            else:
                return

        newSong.prev = currentNode
        newSong.next = currentNode.next
        currentNode.next = newSong

    # Append song(s) into the playlist
    def Append(self, newSong) -> bool:
        # Prevent duplication
        if newSong.file in self.songList:
            return True
        else:
            self.songList.append(newSong.file)

        currentNode = self.head

        if currentNode == None:
            self.head = newSong
        else:
            while(currentNode.next != None):
                currentNode = currentNode.next
            newSong.prev = currentNode
            currentNode.next = newSong       
        self.size += 1
        return False

    # Remove song from the playlist
    def Remove(self,songFile):
        # First, we need to find that node in list
        currentNode = self.head

        if currentNode == None:
            return
        else:
            # Special case: if remove the first element in the list
            if currentNode.file == songFile:
                if(currentNode.next == None):
                    self.head = None
                else:
                    self.head = currentNode.next
            else:
                while(currentNode.file != songFile):
                    currentNode = currentNode.next
       
                currentNode.prev.next = currentNode.next

            # Update the song list
            self.songList.remove(songFile)

    # Get the song at specific index
    def Get(self, index):
        currentNode = self.head

        if currentNode == None:
            return "The List is Empty"
        else:
            for i in range(index):
                if(currentNode.next != None):
                    currentNode = currentNode.next
            
        self.currentSong = currentNode