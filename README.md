# Talk-to-the-cloud
Mainly a speech transcriptor and parser based on nextcloud !

with it you can :
-> Recognize text in audio and write it down
-> Automate parsing of your audio notes on your phone and directly get it in your written notes (Nextcloud account needed)

# SpeechRecognition
The first aim of this project was to build an easy of use tool to write down speech of audio files saved localy.

To do this, you can just run the app and import your files, play it, see what Google Speech Recognition found in it.
(in the beginning, I wanted to use local speech recognition, but unfortunately, without success. Might give another try in the futur)

Then, you can modify what got found and compare to the audio file by playing it (Yes even the almighty google isn't flawless for this kind of tasks), and then save it. 

# GUI

User interface has been made using QT Designer, nothing fancy at all, but at least it works.

# Nextcloud Compatibility

The last module added was a Nextcloud compatibility, here's how it's meant to be used. Create an automatic send of your audio files from your phone or anything else to your own nextcloud. Then, go in preferences of the app and be carefull to set everything properly. (you'll need to specify a folder where temporarly files will be downloaded, unless they will be stored in /tmp, causing their destruction maybe too soon to be used)

# Class names
Set and choose some class names to parse your audio with it. Your audio has to begin with this name (withing first 2 seconds, this delay can be changed in the code). Then, when the audio will be read by the app, it will be sort with that name. 

# End of sync

When the app finished to read every files in the Nextcloud specified folder, it will show a dialog where you can here every audio and modify what has been found and change the class if needed.
By clicking Valider tout Button, everything will be updated in the nextcloud notes output folder (once again, be carefull to set up everything correctly, otherwise, it might crash)

# Usefull notes

I recommend to execute the build of the app from a terminal to see the log printed in here. As the process of sync is made in the main thread, it might looks as app chashed, but it isn't.

# To go Further

I assume that this code is pretty ugly, and not maintainable at all. In the beginning of this project (one of my first), it wasn't meant to go that far, and I had any clue on how to split code in different files and so on. Furthermore, I had not take profit of what object oriented programmation could have bring in advantages. Next projects will be better, as I grew from this experience !
