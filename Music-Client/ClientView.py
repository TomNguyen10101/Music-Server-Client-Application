# MUSIC PLAYER
# Author: Quan Nguyen
# Start Date: 05/14/2023

import customtkinter
from tkinter import StringVar
from tkinter import PhotoImage
from tkinter import Listbox
from tkinter import CENTER
from tkinter import SINGLE
from tkinter import FLAT
from tkinter import END
from tkinter import filedialog
import pygame
import asyncio
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")
from ClientModel import Playlist, Song
from ClientController import MusicController
import os
import threading

class MusicPlayer:
    def __init__(self, root):

        self.track = StringVar()
        self.track.set("The Music Player")

        # Time Variable(s)
        self.runningTime = StringVar()
        self.songLength = StringVar()
        self.runningTime.set("0:00")
        self.songLength.set("0:00")

        # ListBox Variable(s)
        self.chosenItem = None

        # Using Tkinter module, create a interactive GUI
        self.root = root
        self.root.title("Music Player")
        self.root.geometry("600x500")
        self.pos = 0

        # Color variables
        self.enableClr = "#CD4F39"
        self.disableClr = "#808080"

        # Images
        self.loopImage = PhotoImage(file="Icons\\repeat.png")
        self.backImage = PhotoImage(file="Icons\\previous.png")
        self.playImage = PhotoImage(file="Icons\\play-button-arrowhead.png")
        self.skipImage = PhotoImage(file="Icons\\next.png")
        self.shuffleImage = PhotoImage(file="Icons\\shuffle.png")
        self.pauseImage = PhotoImage(file="Icons\\pause.png")
        self.repeatonceImage = PhotoImage(file="Icons\\repeat-once.png")
        self.speakerImage = PhotoImage(file="Icons\\speaker.png")
        self.muteImage = PhotoImage(file="Icons\\mute-speaker.png")
        self.folderImage = PhotoImage(file="Icons\\folder.png")
        self.addImage = PhotoImage(file="Icons\\add.png")
        self.rmvImage = PhotoImage(file="Icons\\minus.png")
        self.searchImage = PhotoImage(file="Icons\\search.png")

        # Volume Variable
        self.volumn = 100

        # THREADS
        self.onlineThread = None
        self.searchThread = None

        # NEW GUI
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure((0,1), weight=1)

        # Define Font
        font = customtkinter.CTkFont(family="Helvatica",
                                        size = 15,
                                        weight="bold")
        
        self.queuelistFrame= customtkinter.CTkFrame(master=self.root)
        self.queuelistFrame.grid(row=0,column=0,padx=20, columnspan=2, pady=(20,0), sticky="nsew")

        self.queuelistFrame.grid_rowconfigure(0, weight=1)
        self.queuelistFrame.grid_columnconfigure((0, 2), weight=1)

        # create scrollable textbox
        self.trackTextBox = Listbox(master=self.queuelistFrame,selectmode=SINGLE,font=font,bg="#404040",fg="white",bd=0,activestyle = 'dotbox', relief=FLAT, highlightthickness=0,exportselection = False, state="disabled")
        self.trackTextBox.grid(row=0, column=1, columnspan=2,sticky="nsew")
        self.trackTextBox.bind("<Double-1>", self.doubleClickEvent)

        # create CTk scrollbar
        self.scrollbar = customtkinter.CTkScrollbar(master=self.queuelistFrame, command=self.trackTextBox.yview)
        self.scrollbar.grid(row=0, column=3, sticky="ns")
        # connect textbox scroll event to CTk scrollbar
        self.trackTextBox.configure(yscrollcommand=self.scrollbar.set)

        self.addSongBtn = customtkinter.CTkButton(master=self.queuelistFrame,text="", width=40, height=40,hover_color="#fff", fg_color="#CD4F39",image=self.addImage,command=self.AddSong)
        self.addSongBtn.place(relx=0.07 , rely=0.09, anchor=CENTER)

        self.addListBtn = customtkinter.CTkButton(master=self.queuelistFrame,text="", width=40, height=40,hover_color="#fff", fg_color="#CD4F39",image=self.folderImage,command=self.AddPlayList)
        self.addListBtn.place(relx=0.17 , rely=0.09, anchor=CENTER)

        self.rmvSongBtn = customtkinter.CTkButton(master=self.queuelistFrame,text="", width=40, height=40,hover_color="#fff", fg_color="#CD4F39",command=self.RemoveSong,image=self.rmvImage)
        self.rmvSongBtn.place(relx=0.27 , rely=0.09, anchor=CENTER)

        # Go Online Button
        self.onlineBtn = customtkinter.CTkButton(master=self.queuelistFrame, width=155, height=40,hover_color="#fff", fg_color="#CD4F39")
        self.onlineBtn.place(relx=0.17 , rely=0.25, anchor=CENTER)
        self.onlineBtn.configure(text="Go Online", text_color="black",font=("Helvatica",17))
        self.onlineBtn.configure(command=lambda: self.RunOnlineThread() if self.onlineBtn.cget('state') == 'normal' else None)

        # Entry Box for searching song
        self.searchBox = customtkinter.CTkEntry(master=self.queuelistFrame, placeholder_text="Type a song",width=110, height=40)
        self.searchBox.place(relx=0.13 , rely=0.40, anchor=CENTER)
        self.searchBox.configure(state="disable")

        # Search Button
        self.searchBtn = customtkinter.CTkButton(master = self.queuelistFrame,text="",width=40, height=40,hover_color="#fff", fg_color="#CD4F39",image=self.searchImage)
        self.searchBtn.place(relx=0.27 , rely=0.40, anchor=CENTER)
        self.searchBtn.configure(state="disable", fg_color= "#808080", command=self.RunSearchThread)

        self.controllerFrame = customtkinter.CTkFrame(master=root, height=70, width=570)
        self.controllerFrame.grid(row=3,column=0,padx=20,pady=5,sticky="nsew")

        self.statusFrame = customtkinter.CTkFrame(master=root, height=35, width=100,fg_color="transparent")
        self.statusFrame.grid(row=2,column=0, padx = 80, pady=5, sticky="nsew")

        self.trackLabel = customtkinter.CTkLabel(master=root, textvariable=self.track,font=font)
        self.trackLabel.grid(row=1,column=0, pady=10, sticky="nsew")

        self.statusFrame.grid_rowconfigure(0, weight=1)
        self.statusFrame.grid_columnconfigure((0, 2), weight=1)

        self.timeBar = customtkinter.CTkProgressBar(master=self.statusFrame, orientation="horizontal",progress_color="#CD4F39")
        self.timeBar.grid(row=0,column=1)

        self.timeRunning = customtkinter.CTkLabel(master=self.statusFrame, textvariable=self.runningTime)
        self.timeRunning.grid(row=0,column=0)

        self.songTime = customtkinter.CTkLabel(master=self.statusFrame, textvariable=self.songLength)
        self.songTime.grid(row=0,column=2)

        self.BackBtn = customtkinter.CTkButton(master=self.controllerFrame, text="",image=self.backImage, width=30, height=30,fg_color="transparent",hover_color="#CD4F39",command=self.BackwardButtonClick)
        self.BackBtn.place(relx=0.25, rely=0.5, anchor=CENTER)

        self.playBtn= customtkinter.CTkButton(master=self.controllerFrame,text="",image=self.playImage, width=30, height=30,fg_color="transparent",hover_color="#CD4F39",command=self.PlayButtonClick)
        self.playBtn.place(relx=0.38 , rely=0.5, anchor=CENTER)

        self.SkipBtn = customtkinter.CTkButton(master=self.controllerFrame, text="",image=self.skipImage, width=30, height=30,fg_color="transparent",hover_color="#CD4F39",command=self.ForwardButtonClick)
        self.SkipBtn.place(relx=0.51 , rely=0.5, anchor=CENTER)

        self.ShuffleBtn = customtkinter.CTkButton(master=self.controllerFrame, text="", width=30, height=30,image=self.shuffleImage,command=self.ShuffleButtonClick,fg_color="transparent",hover_color="#CD4F39")
        self.ShuffleBtn.place(relx=0.10, rely=0.5, anchor=CENTER)

        self.LoopBtn = customtkinter.CTkButton(master=self.controllerFrame, text="", image=self.loopImage, width=30, height=30,fg_color="transparent",command=self.LoopButtonClick, hover_color="#CD4F39")
        self.LoopBtn.place(relx=0.64, rely=0.5, anchor=CENTER)

        self.volBtn = customtkinter.CTkButton(master=self.controllerFrame, text="", image=self.speakerImage, width=30, height=30,fg_color="transparent",command=self.SpeakerButtonClick, hover_color="#CD4F39")
        self.volBtn.place(relx=0.75, rely=0.5, anchor=CENTER)

        self.volumnSlider = customtkinter.CTkSlider(master=self.controllerFrame,width=100,from_=0,to=100,command=self.VolumnChange,progress_color="#CD4F39", button_color="#CD4F39", button_hover_color="#CD4F39")
        self.volumnSlider.place(relx=0.88, rely=0.5, anchor=CENTER)
        self.volumnSlider.set(self.volumn)

        # Init MusicController
        kwargs = {"root":self.root,"trackTextBox":self.trackTextBox,"playButton":self.playBtn,"playImg":self.playImage, "pauseImg":self.pauseImage,"track":self.track,
                  "onlBtn":self.onlineBtn,"searchBox":self.searchBox,"searchBtn": self.searchBtn}

        self.musicController = MusicController(**kwargs)

        self.pop = customtkinter.CTkToplevel(self.root)
    ###################################### NETWORKING GUI ######################################
    def RunOnlineThread(self):
        self.onlineThread = threading.Thread(target=self.GoOnlineButtonClick,daemon=True)
        self.onlineThread.start()

    def GoOnlineButtonClick(self):
        # If Offline 
        if not self.musicController.isConnected:
            self.SetStateButton([self.addSongBtn, self.addListBtn, self.rmvSongBtn], "disable")

            if not self.musicController.ConnectToServer():
                self.SetStateButton([self.addSongBtn, self.addListBtn, self.rmvSongBtn, self.onlineBtn], "normal")
            else:
                self.trackTextBox.delete(0, END) # Clear the tracks box

        # If Online
        else:
            self.musicController.GoOffline()
            self.onlineBtn.configure(text="Go Online")
            self.track.set("The Music Player")
            self.searchBtn.configure(state="disable", fg_color = self.disableClr)
            self.searchBox.configure(state="disable")
            self.musicController.ClearPlaylist()
            self.trackTextBox.delete(0, END)    # Clear the tracks box
                        
    def RunSearchThread(self):
        self.searchThread = threading.Thread(target=self.searchButtonClick, daemon=True)
        self.searchThread.start()

    def searchButtonClick(self):
        if self.searchBtn.cget('state') == "normal":
            self.searchBtn.configure(state="disable",fg_color= "#808080")
            self.onlineBtn.configure(state="disable",fg_color= "#808080")

            songToFind = self.searchBox.get()
            if songToFind != "":
                self.musicController.SearchSong(self.searchBox.get())

            self.searchBtn.configure(state="normal",fg_color= "#CD4F39")
            self.onlineBtn.configure(state="normal",fg_color= "#CD4F39")

    #############################################################################################
    def SetStateButton(self, buttons, state):
        for button in buttons:
            button.configure(state=state, fg_color = self.disableClr if state == "disable" else self.enableClr)

    # When play button clicked, run these methods
    def PlayButtonClick(self):
        self.musicController.Play()
        root.after(100, self.musicController.CheckSongStatus, root)
        root.after(100, self.GetTime, root)

    # When Backward Button clicked, call this method
    def BackwardButtonClick(self):
        self.musicController.Backward()

    # When Forward button clicked, call this method
    def ForwardButtonClick(self):
        self.musicController.Forward()

    # Changing value of sound volume
    def VolumnChange(self, value):
        self.musicController.AdjustVolume(value)

    # Custom Handler for double click event on the ListBox
    def doubleClickEvent(self,event):
        self.isRunning = False
        index = self.trackTextBox.curselection()
        if index:
            selectedIndex = index[0]
            self.musicController.prevIndex = self.musicController.currIndex
            self.musicController.currIndex = selectedIndex

            if(self.musicController.GetCurrentSong() is None):
                self.musicController.GetIndex(selectedIndex)
                self.PlayButtonClick()
            else:
                self.musicController.GetIndex(selectedIndex)
                self.musicController.Play()
        
        # Clear the selection in the listbox
        self.trackTextBox.selection_clear(0, self.trackTextBox.size()-1)

    # Enable/Disable Shuffle Mode
    def ShuffleButtonClick(self):
        if self.shuffle == False:
            self.shuffle = True
            self.ShuffleBtn.configure(fg_color="#CD4F39")           
        else:
            self.shuffle = False
            self.ShuffleBtn.configure(fg_color="transparent")
    
    # Enable/Disable Loop, Single Loop
    def LoopButtonClick(self):
        if self.loopState < 2:
            self.loopState += 1
        else:
            self.loopState = 0

        match(self.loopState):
            case 0:
                self.loop = False
                self.singleLoop = False
                self.LoopBtn.configure(image=self.loopImage)
                self.LoopBtn.configure(fg_color="transparent")    
            case 1:
                self.loop = True
                self.LoopBtn.configure(fg_color="#CD4F39")
            case 2:
                self.singleLoop = True
                self.LoopBtn.configure(image=self.repeatonceImage)

    # Mute/Unmute
    def SpeakerButtonClick(self):
        if self.mute:
            pygame.mixer.music.set_volume(self.musicController.preVol)
            self.volBtn.configure(image=self.speakerImage)
            self.mute = False
            self.volumnSlider.set(self.musicController.preVol * 100)
        else:
            pygame.mixer.music.set_volume(0)
            self.volBtn.configure(image=self.muteImage)
            self.mute = True
            self.volumnSlider.set(0)

    # Add (playlist) folder to the program
    def AddPlayList(self):
        self.trackTextBox.configure(state="normal")
        if self.addListBtn.cget("state") == 'normal':
            #Ask for the folder that contains music files, and add those to the playlist
            try:
                folderPath = filedialog.askdirectory(title="Choose a music folder")
                os.chdir(folderPath)
                songtracks = os.listdir()
                for i, track in enumerate(songtracks):
                    newSong = Song(track,True)
                    isDuplicate = self.musicController.AddToPlaylist(newSong)
                    if not isDuplicate:
                        self.trackTextBox.insert(END, f"{i + 1}. {track}")
            except Exception as e:
                print(f"{e}")
    
    # Add specific mp3 file to the program
    def AddSong(self):
        self.trackTextBox.configure(state="normal")
        if self.addSongBtn.cget("state") == 'normal':
            try:
                filePath = filedialog.askopenfile(title="Choose a MP3 file",mode='r')
                file = os.path.abspath(filePath.name)
                track = os.path.basename(filePath.name)
                isDuplicate = self.musicController.AddToPlaylist(Song(file=file,offline=True))
                if not isDuplicate:
                    self.trackTextBox.insert(END, f"{self.musicController.GetPlaylistSize()}. {track}")
            except Exception as e:
                print(f"{e}")

    # Remove the choosing song from the listbox
    def RemoveSong(self):
        if self.rmvSongBtn.cget("state") == 'normal':
            index = self.trackTextBox.curselection()
            if index:
                self.chosenItem = index[0]
                song = self.trackTextBox.get(self.chosenItem)
                spaceIndex = song.find(' ')
                self.musicController.RemoveFromPlayList(song[spaceIndex + 1:])

                # Display the new playlist after removing
                self.trackTextBox.delete(0,END)
                for i, track in enumerate(self.musicController.GetSongList()):
                    self.trackTextBox.insert(END, f"{i + 1}. {track}")

    # Display the song playtime on the GUI and update the progress bar
    def GetTime(self, root):
        if self.musicController.isRunning:
            # Display Time 
            currentTimeInSec = pygame.mixer.music.get_pos()/1000
            min, sec = divmod(currentTimeInSec, 60)
            hour, min = divmod(min, 60)

            if(sec < 10):
                currentTime = f"{int(min)}:0{int(sec)}"
            else:
                currentTime = f"{int(min)}:{int(sec)}"
            
            self.runningTime.set(currentTime)
            self.songLength.set(self.musicController.GetCurrentSong().songLength)

            # Update the progress bar
            progress = currentTimeInSec / self.musicController.GetCurrentSong().lengthInSec
            self.timeBar.set(progress)

        root.after(50, self.GetTime, root)
    
    # Run the app
    def Run(self):
        self.root.mainloop()

# TODO: Make a Pop Up Window for setting configuration
# TODO: Implement download button for users to download the music got from server to their local machine
# TODO: Unit testing for the server


if __name__ == "__main__":
    root = customtkinter.CTk()
    musicPlayer = MusicPlayer(root)
    musicPlayer.Run()