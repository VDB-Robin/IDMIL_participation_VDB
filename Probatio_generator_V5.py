#%% Variables


abs_path_to_the_project = 'D:/END_OF_STUDY_WORK/'
preselected_midi_port = 'loopMIDI Port 1'



#%% Importations


print('Importing libraries...\n')

import os
import time
import sys
import mido
import pygame

try:
    import numpy as np
    # import tensorflow.compat.v1 as tf   <-- old notation
    import tensorflow.compat.v1.estimator as tf

    from tensor2tensor import models
    from tensor2tensor import problems
    from tensor2tensor.data_generators import text_encoder
    from tensor2tensor.utils import decoding
    from tensor2tensor.utils import trainer_lib

    from magenta.models.score2perf import score2perf
    import note_seq

except:
    import numpy as np
    # import tensorflow.compat.v1 as tf   <-- old notation
    import tensorflow.compat.v1.estimator as tf

    from tensor2tensor import models
    from tensor2tensor import problems
    from tensor2tensor.data_generators import text_encoder
    from tensor2tensor.utils import decoding
    from tensor2tensor.utils import trainer_lib

    from magenta.models.score2perf import score2perf
    import note_seq

from threading import Thread
from queue import Queue

print('\nImports: Done!')



#%% Small functions useful to others


# Upload a MIDI file and convert to NoteSequence.
def upload_midi(data):
  return note_seq.midi_to_note_sequence(data)


# Decode a list of IDs.
def decode(ids, encoder):
    ids = list(ids)
    if text_encoder.EOS_ID in ids:
        ids = ids[:ids.index(text_encoder.EOS_ID)]
    return encoder.decode(ids)



#%% Setup - Piano Performance Language Model


model_name = 'transformer'
hparams_set = 'transformer_tpu'
ckpt_path = abs_path_to_the_project + 'checkpoints_IA/unconditional_model_16.ckpt'

class PianoPerformanceLanguageModelProblem(score2perf.Score2PerfProblem):
    @property
    def add_eos_symbol(self):
        return True

problem = PianoPerformanceLanguageModelProblem()
unconditional_encoders = problem.get_feature_encoders()

# Set up HParams.
hparams = trainer_lib.create_hparams(hparams_set=hparams_set)
trainer_lib.add_problem_hparams(hparams, problem)
hparams.num_hidden_layers = 16
hparams.sampling_method = 'random'

# Set up decoding HParams.
decode_hparams = decoding.decode_hparams()
decode_hparams.alpha = 0.0
decode_hparams.beam_size = 1

# Create Estimator.
run_config = trainer_lib.create_run_config(hparams)
estimator = trainer_lib.create_estimator(
    model_name, hparams, run_config,
    decode_hparams=decode_hparams)

# Create input generator (so we can adjust priming and
# decode length on the fly).
def input_generator():
    global targets
    global decode_length
    while True:
        yield {
            'targets': np.array([targets], dtype=np.int32),
            'decode_length': np.array(decode_length, dtype=np.int32)
        }

# These values will be changed by subsequent cells.
targets = []
decode_length = 0

# Start the Estimator, loading from the specified checkpoint.
input_fn = decoding.make_input_fn_from_generator(input_generator())
unconditional_samples = estimator.predict(
    input_fn, checkpoint_path=ckpt_path)

# "Burn" one.
_ = next(unconditional_samples)



#%% Generation functions


def Generation_from_scratch(numero):
    targets = []
    decode_length = 1024

    # Generate sample events.
    sample_ids = next(unconditional_samples)['outputs']

    # Decode to NoteSequence.
    midi_filename = decode(
        sample_ids,
        encoder=unconditional_encoders['targets'])
    unconditional_ns = note_seq.midi_file_to_note_sequence(midi_filename)

    # Download Performance as MIDI
    name4download = abs_path_to_the_project + 'generated_sequences/GenfS_' + str(numero) + '.mid'
    note_seq.sequence_proto_to_midi_file(unconditional_ns, name4download)

#____________________

def Generation_continuation(numero, filename_imported):
    # CHOOSE PRIMING SEQUENCE

    # Use
    primer_ns = note_seq.midi_file_to_note_sequence(filename_imported)

    # Handle sustain pedal in the primer.
    primer_ns = note_seq.apply_sustain_control_changes(primer_ns)

    # Trim to desired number of seconds.
    max_primer_seconds = 120
    if primer_ns.total_time > max_primer_seconds:
        primer_ns = note_seq.extract_subsequence(
            primer_ns, 0, max_primer_seconds)

    # Remove drums from primer if present.
    if any(note.is_drum for note in primer_ns.notes):
        print('Primer contains drums; they will be removed.')
        notes = [note for note in primer_ns.notes if not note.is_drum]
        del primer_ns.notes[:]
        primer_ns.notes.extend(notes)

    # Set primer instrument and program.
    for note in primer_ns.notes:
        note.instrument = 1
        note.program = 0

    # GENERATE CONTINUATION

    targets = unconditional_encoders['targets'].encode_note_sequence(primer_ns)

    # Remove the end token from the encoded primer.
    targets = targets[:-1]

    decode_length = max(0, 4096 - len(targets))
    if len(targets) >= 4096:
        print('Primer has more events than maximum sequence length; nothing will be generated.')

    # Generate sample events.
    sample_ids = next(unconditional_samples)['outputs']

    # Decode to NoteSequence.
    midi_filename = decode(
        sample_ids,
        encoder=unconditional_encoders['targets'])
    ns = note_seq.midi_file_to_note_sequence(midi_filename)

    # Append continuation to primer.
    continuation_ns = note_seq.concatenate_sequences([primer_ns, ns])

    # _____Download Continuation as MIDI

    name4download = abs_path_to_the_project + 'generated_sequences/Continuation_' + str(numero) + '.mid'
    note_seq.sequence_proto_to_midi_file(continuation_ns, name4download)



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
                print("You don't have an operational MIDI port, sorry.")
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



#%% Option record


def Record_exploitation():
    # Verification of the presence of available records.
    continuous_record = False
    inspiration_list = []
    for inspiration in os.listdir(abs_path_to_the_project + 'record/'):
        if inspiration.endswith(".mid"):
            inspiration_list.append(inspiration)
    if len(inspiration_list) == 0:
        print("\nGenerator option unavailable. You do not have any records to extend.")
        return("CaVaPasEtrePossible")
    else:

        # Selection of the record to be extended
        while True:
            print('\nRecord(s) detected:')
            valid = False
            i = 0
            for inspiration in inspiration_list:
                i += 1
                print("\t", i, ". ", inspiration)
            print("Which recording do you want to use? Please enter its number:")
            alors_qu_est_ce_qu_on_veut = input()
            try:
                alors_qu_est_ce_qu_on_veut = int(alors_qu_est_ce_qu_on_veut)
                valid = True
            except:
                print("Incorrect input value")
            if valid:
                if 0 < alors_qu_est_ce_qu_on_veut <= len(inspiration_list):
                    print("\nAll right, let's process this file.")
                    return abs_path_to_the_project + 'record/' + inspiration_list[alors_qu_est_ce_qu_on_veut - 1]
                else:
                    print("Incorrect input value")



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
q_menuR = Queue()
q_volumeR = Queue()
q_record_wait = Queue()



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
        NAME = abs_path_to_the_project + 'generated_sequences/GenfS_' + str(player_position) + '.mid'

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
        NAME = abs_path_to_the_project + 'generated_sequences/GenfS_' + str(player_position) + '.mid'

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
    RECORD = False
    record_wait = True
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
                        print('All right, the record option will start in a few moments.')
                        RECORD = True
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

        # Record mode menu
        while RECORD:
            """
            We will just wait for the other parts of the generator to become
             aware of the switch to record mode before displaying the menu.
            """
            while record_wait:
                time.sleep(0.5)
                if q_record_wait.empty() == False:
                    skip = False
                    record_wait = q_record_wait.get()
                    if record_wait == 'end':
                        skip = True
                        choice_record = '3'
                        record_wait = False
                    if record_wait == 'continuons':
                        record_wait = False

            if q_record_wait.empty() == False:
                record_wait = q_record_wait.get()
                if record_wait == '1instantSVP':
                    record_wait = True
                    skip = True

            if skip == False:
                print("\n______________Record option menu______________")
                print('\t1. Change file to extend\n\t2. Start a new extension on the same file\n\t3. Exit record mode')
                #if output == "audio":
                #    print('\t4. Volume')
                print('Choice:')
                choice_record = input()

            if choice_record == '1':
                q_menuR.put('change')
                print("All right, we'll select another file in a few moments.")
                while q_menuR.empty() == False:
                    time.sleep(0.5)

            if choice_record == '2':
                q_menuR.put('restart')
                print("All right, we'll change that in a few moments.")
                while q_menuR.empty() == False:
                    time.sleep(0.5)

            if choice_record == '3':
                q_record.put(False)
                print("All right, we'll get out of record mode in a few moments.")
                while q_record.empty() == False:
                    time.sleep(0.5)
                RECORD = False
                record_wait = True

            """
            if choice_record == "4" and output == "audio":
                ask = True
                valid = False
                while ask:
                    print('Value (between 0 and 100):')
                    Volume_record = input()
                    try:
                        Volume_record = int(Volume_record)
                        valid = True
                    except:
                        if Volume_record == "return" or Volume_record == "Return" or Volume_record == "RETURN":
                            ask = False
                    if valid:
                        if 0 < Volume_record <= 100:
                            q_volumeR.put(Volume_record / 100)
                            ask = False
                        else:
                            valid = False
            """

            choice_record = '0'



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
numero_cont = 1
VolumeR = 0.5

while True:

    continuous = True
    time.sleep(1)

    while continuous:
        targets = []
        decode_length = 1024
        #print('\nBeginning of generation ', numero_gen, ' !')
        Generation_from_scratch(numero_gen)
        print('\nEnd of generation ', numero_gen, ' !')
        q_numero.put(numero_gen)
        numero_gen += 1
        numero_gen %= 2000   # memory protection (limited number of files)

        # Control of thread variables
        if q_record.empty() == False:
            tmp_record = q_record.get()
            if tmp_record:
                record = True
                continuous = False


    # Alternative options

    if record:
        q_pause.put(True)
        la_totale = True
        menuR = 'rien'
        record_gen_wait = True
        boucle = False

        while record:

            # Creation
            if la_totale:
                ToExtend = Record_exploitation()
                la_totale = False
            if ToExtend == "CaVaPasEtrePossible":
                q_record_wait.put('end')
                boucle = False
                record = False
            if ToExtend != "CaVaPasEtrePossible":
                print("Start of the continuation generation.")
                targets = []
                decode_length = 1024
                Generation_continuation(numero_cont, ToExtend)
                cont2play = abs_path_to_the_project + 'generated_sequences/Continuation_' + str(numero_cont) + '.mid'
                print('Generation on the basis of the record completed.')
                numero_cont += 1
                boucle = True

                if record_gen_wait:
                    q_record_wait.put('continuons')
                    record_gen_wait = False

            # Player
            while boucle:
                if output == "midi":
                    Player_midi2midiStream(outport, cont2play)
                if output == "audio":
                    Player_midi2audio(cont2play, VolumeR)

                # Menu and control of thread variables
                if q_record.empty() == False:
                    if q_record.get() == False:
                        boucle = False
                        record = False
                if q_menuR.empty() == False:
                    menuR = q_menuR.get()
                    if menuR == 'change':
                        boucle = False
                        la_totale = True
                        q_record_wait.put('1instantSVP')
                        record_gen_wait = True
                    if menuR == 'restart':
                        boucle = False
                if q_volumeR.empty() == False:
                    VolumeR = q_volume.get()


        # Exit record mode and restart the generator
        q_pause.put(False)
        record = False
        continuous = True