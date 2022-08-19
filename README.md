# IDMIL_participation_VDB
This repertory consigning all the participations of Robin Vandebrouck on the Probatio project within the framework of his end of studies work.

The main purpose of this participation is related to the creation of an intelligent musical generator that can be used with the Probatio project, another IDMIL project.
The Probatio is a toolkit for the creation of new digital musical instruments. Its two objectives are on the one hand to offer new possibilities for creation, and on the other hand to decrease the cost in time and effort for prototyping. This contribution (and especially the generator) has been designed to enhance these two key objectives.


This GitHub contains several elements, most of which are related to the intelligent music generator. Indeed, only the Bloc_M5 folder is not related to the generator, and contains as its name indicates, the files related to the Probatio block designed to host an M5 module. 
The "Embedded_audio_processing" folder is a complement to the generator and aims at exploiting the Probatio and the generator together with no dependency on a computer. This approach indeed aims at using a Raspberry Pi as a central unit for sound synthesis and interaction management with the Probatio. Due to lack of time, this aspect of the project has not been fully completed. This is why a document in the folder explains the general logic of this point.


## Content

In this directory you will find various elements:

1. __Block_M5__ : Folder containing the STL files to be printed for the conception of the Probatio block maintaining the M5 module.

2. __Embedded_audio_processing__ : Folder containing the processing logic for an embedded aspect of the Probatio interaction logic and the audio synthesis.

3. __Operating_files__ : Folder containing the material necessary for the intelligent music generator to function properly.

4. __Demonstration videos__ : Folder containing a demonstration video of the use of Probatio with the generator.

5. __Probatio_generator_V5.py__ : Python file of the generator.

6. __Probatio_generator_RPi_onlineGen.py__ : Python file of the generator modified for online generation. For its operation, the generation can be placed in any online processing medium, such as Google Colab for example. This code works by analysing the download folder of the device on which this python code is running and will manage the correct creation of the MIDI stream. This code has been verified and successfully run in a proof of concept using Google Colab and a Raspberry Pi.

7. __requierement.txt__ : File explaining all the dependencies and installation needs for the generator to work properly.

8. __Informative presentation.pptx__ : Power point presentation of the participation.

9. __TFE_VANDEBROUCK_Robin.pdf__ : Report describing the participation.


## Use of the generator

*The objective of the generator is the creation of a continuous unpredictable music stream of appreciable quality. The creation of this stream is achieved through the use of artificial intelligence. The output of the generator is either a MIDI or an audio stream (as the generator also has an internal synthesis available, which is very useful in a testing context).*


To make the code work, after installing everything necessary (see requirements), you just have to launch the main python code. Be careful, also to have downloaded the complete "Operating_files" folder. Moreover, it is necessary to change in the code the path to where you have placed this folder (variable abs_path_to_the_project, ligne 4). To save time during the execution it is also advised to change the pre-selected midi port (variable preselected_midi_port, ligne 5).


Also note that in the "Operating_files" folder, you have the "generated_sequences" and "record" folders. The first one will host the creations of the generator and the second one is the folder where you can place small MIDI files for the conditioned mode. As far as the generated files are concerned, you can see that they are an average of one minute long, because the generator works by creating small MIDI files that it uses to create a continuous flow. So, if the user liked a part of the stream, he can find the extract in this folder. Be careful though, the generator writes over the already created files. It is thus necessary to collect the MIDI files before restarting the generator if they interest the user.


Note that it is perfectly possible to re-train a neural network and to continue to use this code. The only thing is to change the trained network in the "Operating_files/checkpoints_IA" and to check its correct referencing in the main code. For more information about the training, see the GitHub pages of the Google Magenta project.


### Generator menu

1. __Loop__ : as the generator creates continuously, it is not initially intended to stagnate on one of the generated sequences. However, thanks to this command the user can ask the system to loop on the sequence he is reading. Once the user is bored of this loop, he can resume the classic sequence path thanks to this same command.
2. __Pause__ : elementary, but useful, the playback can be paused without cutting off the generating part.
3. __Activate the conditioned mode__ : this specific mode consists of using a small MIDI file to extend it. The user thus has the possibility of working on files selected or recorded by himself in the generation process. This continuation thus represents a generation conditioned by a small sequence from the user.
4. __Volume__ : in case the user wants to keep the internal audio synthesis of the generator, he can modify the volume of this audio production.
5. __Turn off the system__ : nothing lasts forever, the user's desire to use the generator is no exception.


## Summary: Make the generator work properly

1. Install everything that is necessary in terms of dependencies (requierement).

2. Download the Operating_files folder.

3. Change the direction in the code to the address of the Operating_files folder in your device (variable abs_path_to_the_project, line 4).

4. Optional: To save time during execution, also replace the variable of the preselected MIDI port (variable preselected_midi_port, line 5).

5. Run the code and install any missing python libraries.

6. If you are using an audio synthesis software, make sure you have opened it and that it is correctly "connected" to the generator thanks to a good MIDI port selection (if needed see LoopMIDI, to create a virtual port on your computer).

7. Enjoy and interact with the menu (to make it reappear in the console, you can press enter at any time).


## Notes

This work is based on "Generating Piano Music with Transformer" by __Ian Simon, Anna Huang, Jesse Engel, Curtis "Fjord" Hawthorne__.

This code lets you play with pretrained [Transformer](https://arxiv.org/abs/1706.03762) models for piano music generation, based on the [Music Transformer](http://g.co/magenta/music-transformer) model introduced by [Huang et al.](https://arxiv.org/abs/1809.04281) in 2018.

The models used here were trained on over 10,000 hours of piano recordings from YouTube, transcribed using [Onsets and Frames](http://g.co/magenta/onsets-frames) and represented using the event vocabulary from [Performance RNN](http://g.co/magenta/performance-rnn).
