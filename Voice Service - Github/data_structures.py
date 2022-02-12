# notgraket
# Data Structures for "main.py"
# Created: 2-8-2022
# Last Edit: 2-12-2022

import speech_recognition as recognition
from queue import Queue
import time, requests, inflect, os
from gtts import gTTS
import winsound
from pydub import AudioSegment



class TextToSpeech:
    def __repr__(self):
        return "<class 'TextToSpeech'>"
    

    def __init__(self, directory):
        self.directory = directory
        self.mp3 = None
        self.wav = None
    

    def say(self, text : str):
        """Uses text-to-speech on an entered string"""
        if (isinstance(text, str)): # Error handeling
            file_id = id(text) # Unique file id based on text
        
            # Locations to temporarily store the files for reading
            self.mp3 =  f"{self.directory}//{file_id}.mp3"
            self.wav = f"{self.directory}//{file_id}.wav"

            gTTS(text=text, lang='en', slow=False).save(self.mp3)
        
            # Convert .mp3 to .wav
            # XXX FIND A MEDIA PLAYER MODULE THAT DOESN'T NEED FILES XXX
            mp3 = AudioSegment.from_mp3(self.mp3)
            mp3.export(self.wav, format = "wav")

            # Windowless media player
            winsound.PlaySound(self.wav, winsound.SND_FILENAME)

            # Clean up folder
            os.remove(self.mp3)
            os.remove(self.wav)





class AudioRecorder:
    def __repr__(self):
        return "<class 'AudioRecorder'>"


    def __init__(self):
        self.Microphone = recognition.Microphone(device_index = 1) # Default for my mic
        self.Recognizer = recognition.Recognizer()
        self.Parser = Parser()
        self.recording = True
    
    def Toggle_Recording(self):
        """Toggles continuous recording on or off"""
        self.recording = not self.recording


    def record(self):
        """Continuously record audio, records for 3 seconds if speech is detected"""
        while True:
            if (self.recording == True):
                with self.Microphone as source:
                    Audio = self.Recognizer.listen(source, phrase_time_limit = 3, timeout = None)
                    self.Parser.queue.put(Audio)





class Parser:
    def __repr__(self):
        return "<class 'Parser'>"


    def __init__(self):
        self.queue = Queue(maxsize = 0)
        self.Recognizer = recognition.Recognizer()
        self.container = {}
    

    def parse(self) -> list:
        """Parses next audio object in queue"""
        try:
            if (self.queue.qsize() > 0):
                Audio = self.queue.get()
                command = self.Recognizer.recognize_google(Audio).lower().split()
                return command

        except recognition.UnknownValueError: # recording silence
            pass
    

    def parse_arguments(self, arguments, num) -> list:
        return arguments[0:num]


    def execute(self):
        """Executes functions based on commands from parsed audio objects"""
        while True:
            try:
                command = self.parse() # get function and arguments
                cmd_keyword = command[0]

                if (cmd_keyword in self.container):

                    expected_arg_types = self.container[cmd_keyword]["expected"] # Expected argument data types for the given keyword
                    args_received = command[1 : len(expected_arg_types) + 1] # Received arguments
                    received_arg_types = [type(arg) for arg in args_received] # Data types of received arguments, ex: [str, int]
                    cmd_function = self.container[cmd_keyword]["function"] # Function of given keyword
                    num_args_expected = len(expected_arg_types) # Number of arguments expected for the given keyword
                    
                    
                    if (num_args_expected == 0):
                        cmd_function()

                    elif (received_arg_types == expected_arg_types):
                        cmd_function(args_received)

                    time.sleep(0.01) # Save CPU resources

            except TypeError: # No Object in Queue
                pass

            except KeyError: # Non-existant command
                pass 
    

    def compare(self, keyword : str, arguments : list) -> bool:
        """Compares given arguments against expected arguments"""
        received = [type(arg) for arg in arguments]
        expected = self.container[keyword]["expected"]
        return (received == expected)





class Dictionary:
    def __repr__(self):
        return "<class 'Dictionary'>"
    

    def __init__(self):
        self.Engine = inflect.engine()
        self.Cache = Cache(maxsize=20)
        # Change to your resources folder
        self.TTS = TextToSpeech(directory = "C:\\Users\\<username>\\Desktop\\Projects\\Voice Service\\Voice Service 1\\resources")
    

    def get_data(self, word):
        """Caches api data for entered word"""
        if isinstance(word, int):
            word = self.Engine.number_to_words(word)
        
        if (word not in self.Cache):
            try:
                data = requests.get("https://api.dictionaryapi.dev/api/v2/entries/en/" + word).json()
                self.Cache.add(word, data)
            
            except requests.exceptions.ConnectionError: # No Internet Connection
                print("No connection to API service...")


    def get_definition(self, word : str):
        """Returns the definition of a word"""
        #word = word.lower()
        self.get_data(word)

        try:
            word_data = self.Cache[word][0]['meanings'][0]
            definition = word_data['definitions'][0]['definition']

            text = f"""{word.capitalize()} - {definition}"""
            self.TTS.say(text)
            

        except KeyError: # Occurs when misspelling the word
            pass







class Cache:
    def __init__(self, maxsize):
        self.items = {}
        self.maxsize = maxsize
    

    def __repr__(self):
        return f"Cache[{self.items}]"

    
    def __len__(self):
        """Allows len() to reference self.items"""
        return len(self.items)
    

    def __contains__(self, value):
        """Allows checking for membership against self.items"""
        return value in self.items
    

    def __getitem__(self, value):
        """Allows the setting or calling of values identically to dictionaries"""
        if value in self.items:
            return self.items[value]


    def add(self, key, value):
        """Adds an item to the Cache"""
        """Automatically deletes oldest item in cache if (len > maxsize) and maxsize is defined"""
        self.items[key] = value
        if (self.maxsize != None) and (len(self.items) > self.maxsize):
            del self.items[next(iter(self.items))]
            

    def remove(self, key):
        """Removes an item from the Cache if it exists"""
        if key in self.items:
            del self.items[key]

    




