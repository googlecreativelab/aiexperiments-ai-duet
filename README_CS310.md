***Detecting Emotions in Music***
**Thomas, Avi, and Avery**

To extend the AI Duet program we added an extra step to the preexisting flow of music data from the client to the server, and back to the client.

The files modified were:
-server/server.py
-server/savedModels/*
-server/usingMusicNN.py
-static/src/ai/AI.js
-static/src/interface/Glow.js
-static/src/style/common.scss
-static/src/style/glow.css



**To create a music sentiment detection model:**

  ***-Store happy/sad songs in seperate folders.***
  
  ***-Run XXX path/to/folder/with/midi/files***
    (This will generate a text file with the notes normailized to the C and c minor scales, and represents the notes as numbers.)
    
  ***-Run createMusicalFeatureSets.py***
    (This takes the text files and generates musical feature sets, which is the input data of frequencies of notes, and the labels for each set of note frequencies. This is then saved as a pickle, with the testing and training data sepearated)
    
  ***-Run trainMusicNN.py***
    (This takes the pickle created and passes the data through a NN. It saves the NN's weights as a model)
    
 
 
**To use the sentiment detection model to classify a song according it its sentiment:**

  ***-Run usingMusicNN.py***
    (This takes the sentiment detection model and a midi file. It converts the MIDI file to a feature set of fequencies, which it passes through the trained NN. It prints the classification of the set.)
    
    
