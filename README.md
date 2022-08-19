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

6. __Probatio_generator_RPi_onlineGen.py__ : Python file of the generator modified for online generation. For its operation, the generation can be placed in any online processing medium, such as Google Colab for example. This code works by analysing the download folder of the device on which this python code is running and will manage the correct creation of the midi stream.

7. __requierement.txt__ : File explaining all the dependencies and installation needs for the generator to work properly.

8. __Informative presentation.pptx__ : Power point presentation of the participation.

9. __TFE_VANDEBROUCK_Robin.pdf__ : Report describing the participation.


## Use of the generator

*The objective of the generator is the creation of a continuous unpredictable music stream of appreciable quality. The creation of this stream is achieved through the use of artificial intelligence. The output of the generator is either a MIDI or an audio stream (as the generator also has an internal synthesis available, which is very useful in a testing context).*


## Notes

This work is based on "Generating Piano Music with Transformer" by __Ian Simon, Anna Huang, Jesse Engel, Curtis "Fjord" Hawthorne__.

This code lets you play with pretrained [Transformer](https://arxiv.org/abs/1706.03762) models for piano music generation, based on the [Music Transformer](http://g.co/magenta/music-transformer) model introduced by [Huang et al.](https://arxiv.org/abs/1809.04281) in 2018.

The models used here were trained on over 10,000 hours of piano recordings from YouTube, transcribed using [Onsets and Frames](http://g.co/magenta/onsets-frames) and represented using the event vocabulary from [Performance RNN](http://g.co/magenta/performance-rnn).
