#%% Variables


abs_path_to_the_project = 'D:/END_OF_STUDY_WORK/'
preselected_midi_port = 'loopMIDI Port 1'
production_path = '/'



#%% Importations


print('Importing libraries...\n')

import time
import sys
import os
import mido
import pygame

from threading import Thread
from queue import Queue

print('\nImports: Done!')



#%% MIDI player


def Setup_MIDI_port(selected_MIDI_port=preselected_midi_port):
    print('\nAvailable MIDI port(s) on the device :')
    print(mido.get_output_names())
    try:
        OUTPORT = mido.open_output(selected_MIDI_port)
        print('Selected MIDI port : ' + selected_MIDI_port)
    except:
        try:
            OUTPORT = mido.open_output(mido.get_output_names()[0])
            print('Selected MIDI port : ' + mido.get_output_names()[0])
        except:
            if len(mido.get_output_names()) == 0:
                print("You don t have an operational MIDI port, sorry.")
                sys.exit(1)
            else:
                print("Problem detected with the MIDI port : " + mido.get_output_names()[0])
                sys.exit(1)
    return OUTPORT


def Player_midi2midiStream(OUTPORT, midi_filename):
    for msg in mido.MidiFile(midi_filename).play():
        OUTPORT.send(msg)



#%% AUDIO player


def play_music(midi_filename):
    clock = pygame.time.Clock()
    pygame.mixer.music.load(midi_filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        clock.tick(30)


def Setup_audio():
    # mixer config
    freq = 44100  # audio CD quality
    bitsize = -16  # unsigned 16 bit
    channels = 2  # 1 is mono, 2 is stereo
    buffer = 1024  # number of samples
    pygame.mixer.init(freq, bitsize, channels, buffer)


def Player_midi2audio(midi_filename, volume=0.5):
    # optional volume 0 to 1.0
    pygame.mixer.music.set_volume(volume)

    # listen for interruptions
    try:
        # use the midi file you just saved
        mid = mido.MidiFile(midi_filename)
        # print("Lecture d'un fichier d'une longueur de : ", mid.length, "secondes !")
        play_music(midi_filename)
    except KeyboardInterrupt:
        # if user hits Ctrl/C then exit
        # (works only in console mode)
        pygame.mixer.music.fadeout(1000)
        pygame.mixer.music.stop()
        raise SystemExit



#%% Welcome function


def Welcome():
    print('\n\n_________________________________________')
    print('\nWelcome to the generator menu sweet user!')
    init = True
    while init:
        print('\nFirst of all, do you want a MIDI generation or an audio generation?\n\t1. MIDI\n\t2. Audio\nYour choice:')
        output_type = input()
        if output_type == "1" or output_type == "MIDI" or output_type == "midi":
            output_type = "midi"
            init = False
        elif output_type == "2" or output_type == "Audio" or output_type == "audio":
            output_type = "audio"
            init = False
        else:
            print("I don't think I gave you that option...")
    return output_type



#%% Generation control function


def Initialization_4_prod_analysis(target_path):
    tmp = 0
    for condamne in os.listdir(target_path):
        if condamne.endswith(".mid"):
            os.remove(condamne)
            tmp += 1
    print('\nInitialization of the recovery folder : ', tmp, 'deleted MIDI file(s).')


def Production_analysis(target_path):
    production_list = []
    for product in os.listdir(target_path):
        if product.endswith(".mid"):
            production_list.append(product)
    return len(production_list)



#%% Initialization of thread variables


q_numero = Queue()
q_loop = Queue()
q_loop.put(False)
q_pause = Queue()
q_pause.put(False)
q_record = Queue()
q_record.put(False)
q_volume = Queue()
q_volume.put(0.5)



#%% Definitions of threading functions


def PlayerMidiStreamThread(q_numero, q_loop, q_pause, out):
    # Initialization of local variables
    numero = 0
    player_position = 0
    loop = False
    flag = False

    while True:

        # Control of thread variables
        if q_numero.empty() == False:
            numero = q_numero.get()
        if q_loop.empty() == False:
            loop = q_loop.get()
        if q_pause.empty() == False:
            pause = q_pause.get()

        # Start playing only after the first two sequences have been created
        if numero == 0 and flag == False:
            time.sleep(0.5)
            print('\nGeneration of the first sequences (0/2).')
            print('The playback will start after the generation of these first two sequences.')
            flag = True
        if numero == 1 and flag == True:
            time.sleep(0.5)
            print('\nGeneration of the first sequences (1/2).')
            print('The playback will start after the generation of these first two sequences.')
            flag = False
        if numero == 2:
            player_position = 1

        # Updating the file name to read
        NAME = production_path + 'GenfS_' + str(player_position) + '.mid'

        # Reading and preparation of the next file if existing
        if player_position < numero and loop == False and pause == False:
            player_position += 1
        if player_position >= 2 and pause == False:
            print('\nPlaying the file : ' + 'GenfS_' + str(player_position - 1) + '.mid')
            Player_midi2midiStream(out, NAME)

#____________________

def PlayerAudioThread(q_numero, q_loop, q_pause, q_volume):
    # Initialization of local variables
    volume = 0.5
    numero = 0
    player_position = 0
    loop = False
    flag = False

    while True:

        # Control of thread variables
        if q_volume.empty() == False:
            volume = q_volume.get()
            print('Volume change taken into account --> Volume : ', volume * 100)
        if q_numero.empty() == False:
            numero = q_numero.get()
        if q_loop.empty() == False:
            loop = q_loop.get()
        if q_pause.empty() == False:
            pause = q_pause.get()

        # Start playing only after the first two sequences have been created
        if numero == 0 and flag == False:
            time.sleep(0.5)
            print('\nGeneration of the first sequences (0/2).')
            print('The playback will start after the generation of these first two sequences.')
            flag = True
        if numero == 1 and flag == True:
            time.sleep(0.5)
            print('\nGeneration of the first sequences (1/2).')
            print('The playback will start after the generation of these first two sequences.')
            flag = False
        if numero == 2:
            player_position = 1

        # Updating the file name to read
        NAME = production_path + 'GenfS_' + str(player_position) + '.mid'

        # Reading and preparation of the next file if existing
        if player_position < numero and loop == False and pause == False:
            player_position += 1
        if player_position >= 2 and pause == False:
            print('\nPlaying the file : ' + 'GenfS_' + str(player_position - 1) + '.mid')
            Player_midi2audio(NAME, volume)
            time.sleep(2)

#____________________

def MenuThread(q_loop, q_record, q_pause, out):
    PAUSE = False
    while True:
        print('\nWhich option do you want to change (enter the option number)?')
        print('\t1. Activate the loop')
        if PAUSE == False:
            print('\t2. Pause the playback')
        if PAUSE:
            print('\t2. Restart the playback')
        print('\t3. Recording mode')
        if out == "audio":
            print('\t4. Volume')
        print('\tF. Turn off the generator')
        print('Your choice:')
        choice = input()
        if out == "midi" and choice != "1" and choice != "2" and choice != "3" and choice != "F" and choice != "f":
            print("I don't think I gave you that option...")
        if out == "audio" and choice != "1" and choice != "2" and choice != "3" and choice != "4" and choice != "F" and choice != "f":
            print("I don't think I gave you that option...")
        if (out == "midi" and (choice == "1" or choice == "2" or choice == "3" or choice != "F" or choice != "f")) or\
                (out == "audio" and (choice == "1" or choice == "2" or choice == "3" or choice == "4" or choice != "F" or choice != "f")):
            if choice == "1":
                ask = True
                while ask:
                    print('Activate: yes / no ?')
                    choice = input()
                    if choice == "yes" or choice == "YES" or choice == "y" or choice == "Y":
                        q_loop.put(True)
                        print('Loop activated !')
                        ask = False
                    if choice == "no" or choice == "NO" or choice == "n" or choice == "N":
                        q_loop.put(False)
                        print('Loop deactivated !')
                        ask = False
            if choice == "2":
                ask = True
                while ask:
                    if PAUSE == False:
                        print('Activate the pause: yes / no ?')
                    if PAUSE:
                        print('Deactivate the pause: yes / no ?')
                    choice = input()
                    if (choice == "yes" or choice == "YES" or choice == "Yes" or choice == "y" or choice == "Y")\
                            and PAUSE == False:
                        q_pause.put(True)
                        PAUSE = True
                        print('All right, the music will stop in a few moments.')
                        ask = False
                    elif (choice == "yes" or choice == "YES" or choice == "Yes" or choice == "y" or choice == "Y")\
                            and PAUSE == True:
                        q_pause.put(False)
                        PAUSE = False
                        print('All right, the music will restart in a few moments.')
                        ask = False
                    if choice == "no" or choice == "NO" or choice == "No" or choice == "n" or choice == "N":
                        ask = False
            if choice == "3":
                ask = True
                while ask:
                    print('Activate: yes / no ?')
                    choice = input()
                    if choice == "yes" or choice == "YES" or choice == "Yes" or choice == "y" or choice == "Y":
                        q_record.put(True)
                        print('All right, the record will start in a few moments.')
                        ask = False
                    if choice == "no" or choice == "NO" or choice == "No" or choice == "n" or choice == "N":
                        ask = False
            if choice == "4" and out == "audio":
                ask = True
                valid = False
                while ask:
                    print('Value (between 0 and 100):')
                    Vchoice = input()
                    try:
                        Vchoice = int(Vchoice)
                        valid = True
                    except:
                        if Vchoice == "return" or Vchoice == "Return" or Vchoice == "RETURN":
                            ask = False
                    if valid:
                        if 0 < Vchoice <= 100:
                            q_volume.put(Vchoice/100)
                            ask = False
                        else:
                            valid = False
            if choice == "F" or choice == "f":
                print('\n\nGoodbye user!')
                sys.exit(1)



#%% Main


# Welcome and output type definition
output = Welcome()

# Start of the functions in parallel
if output == "midi":
    # Initialization of the midi port
    outport = Setup_MIDI_port()
    Tbeta = Thread(target=PlayerMidiStreamThread, args=(q_numero, q_loop, q_pause, outport,))
else:
    Setup_audio()
    Tbeta = Thread(target=PlayerAudioThread, args=(q_numero, q_loop, q_pause, q_volume,))

Tgamma = Thread(target=MenuThread, args=(q_loop, q_record, q_pause, output,))

Tbeta.start()
Tgamma.start()

# Main loop and generation activation
numero_gen = 1

while True:

    continuous = True
    time.sleep(1)
    tmp_size = len(os.listdir(production_path))

    while continuous:

        if tmp_size != len(os.listdir(production_path)):
            numero_gen = Production_analysis(production_path)
            print('\nEnd of generation ', numero_gen, ' !')
        q_numero.put(numero_gen)

        # Control of thread variables
        if q_record.empty() == False:
            tmp_record = q_record.get()
            if tmp_record:
                record = True
                continuous = False

    # Alternative options

    if record:
        print('\nToo bad, this part is not implemented yet.')
        record = False
        continuous = True