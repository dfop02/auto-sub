import os
import sys
import time
import datetime
import logging
import speech_recognition as sr
import moviepy.editor as mp
from textwrap import wrap
from pydub import AudioSegment
from split_on_silence_with_timing import split_on_silence_with_timing
from deep_translator import GoogleTranslator
from pathlib import Path

class AutoSub:
    video_name = None
    audio      = None
    from_lang  = None
    to_lang    = None
    srt_path   = None
    verbose    = True

    def __init__(self, video_path, from_lang='ja', to_lang='pt', srt_path='tmp', verbose=True):
        self.video_name = Path(video_path).stem
        self.audio      = self.get_audio_from_video(video_path)
        self.from_lang  = from_lang
        self.to_lang    = to_lang
        self.srt_path   = self.format_srt_path(srt_path)
        self.verbose    = verbose

    def get_audio_from_video(self, video):
        # open video as a file
        clip = mp.VideoFileClip(video)
        # Set audio path
        audio_path = "tmp/{}.wav".format(self.video_name)
        # Remove audio from video and save as a wav file
        clip.audio.write_audiofile(audio_path, logger='bar' if self.verbose else None)
        # open the audio file stored in the local system as a wav file.
        return AudioSegment.from_wav(audio_path)

    def format_srt_path(self, srt_path):
        if srt_path:
            if srt_path[-1] == '/':
                return srt_path[:-1]
            elif srt_path[-4:] == '.srt':
                return '/'.join(srt_path.split('/')[:-1])
            else:
                return srt_path
        else:
            return None

    # a function that splits the audio file into chunks
    # and applies speech recognition for create subtitles
    def generate_subtitles(self):
        # open a file where we will concatenate and store the subtitle text
        fh = open("{}/{}.srt".format(self.srt_path, self.video_name), "w+")

        if self.verbose:
            print("Creating chunks...", end='', flush=True)
            start = time.perf_counter()

        # split track where silence is 0.5 seconds or more and get chunks
        chunks = split_on_silence_with_timing(self.audio,
            # must be silent for at least 0.5 seconds
            # or 500 ms. adjust this value based on user
            # requirement. if the speaker stays silent for
            # longer, increase this value. else, decrease it.
            min_silence_len = 800,

            # consider it silent if quieter than -16 dBFS
            # adjust this per requirement
            silence_thresh = int(self.audio.dBFS) - 20,

            # amount of silence to leave at the beginning and end of the chunks.
            # Keeps the sound from sounding like it is abruptly cut off.
            keep_silence = 100,

            # Step size for interating over the segment in ms
            seek_step = 1,

            # Return timestamp from chunk (start,end)
            with_timing = True
        )

        if self.verbose:
            end = time.perf_counter()
            print(f'Done.\nChunks created in {(end - start):.2f} seconds\n')

        # create a directory to store the audio chunks.
        os.makedirs('tmp/audio_chunks', exist_ok=True)

        # create and configure a speech recognition object
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 50
        recognizer.dynamic_energy_threshold = False

        # TO-DO: remove ambient noise not working property, possibly should remove it
        # recognizer.adjust_for_ambient_noise(source, duration=0.5)

        # prepare statistics data
        total_chunks       = len(chunks)
        valid_recognize    = 0
        invalid_recognize  = 0
        minimum_chunk_size = 1000

        line_count = 1
        i = 0
        # process each chunk
        for start_clip, end_clip, chunk in chunks:
            # Ignore chunk with less than minimun size
            if len(chunk) < minimum_chunk_size:
                total_chunks -= 1
                continue

            # export audio chunk and save it in
            # the current directory.
            print("Saving chunk{0}.wav".format(i)) if self.verbose else None

            # specify the bitrate to be 192 k
            chunk.export("./tmp/audio_chunks/chunk{0}.wav".format(i), bitrate ='192k', format ="wav")

            # the name of the newly created chunk
            filename = 'tmp/audio_chunks/chunk'+str(i)+'.wav'

            print("Processing chunk "+str(i)) if self.verbose else None

            # recognize the chunk
            with sr.AudioFile(filename) as source:
                audio_listened = recognizer.listen(source)

            try:
                # try converting it to text
                # TO-DO: Add support to from_language variable
                rec    = recognizer.recognize_google(audio_listened, language="ja-JP")
                rec_pt = self.jap_to_pt(rec)
                text   = rec_pt if rec_pt else rec
                print("  " + text) if self.verbose else None
                self.write_to_file(fh, text, line_count, (start_clip, end_clip))
                valid_recognize += 1
                line_count += 1

            # catch any errors.
            except sr.UnknownValueError:
                print("  Could not understand audio") if self.verbose else None
                invalid_recognize+=1

            except sr.RequestError as e:
                print("  Could not request results. check your internet connection") if self.verbose else None
                invalid_recognize+=1

            i += 1

        fh.close()

        if self.verbose:
            print("\n\nTotal Chunks: {}\nValid: {} - {:.2f}%\nInvalid: {} - {:.2f}%".format(
                total_chunks,
                valid_recognize,
                (valid_recognize/total_chunks)*100,
                invalid_recognize,
                (invalid_recognize/total_chunks)*100)
            )

    def jap_to_pt(self, text):
        '''
        Translate the source language (video) to target (srt) using Google Translator
        Args:
            text : text to be translated
        '''
        translated_text = None

        try:
            translated_text = GoogleTranslator(source=self.from_lang, target=self.to_lang).translate(text=text)
        except Exception as e:
            print(str(e))

        return translated_text

    def write_to_file(self, file_handle, inferred_text, line_count, limits):
        '''
        Write the inferred text to SRT file
        Follows a specific format for SRT files
        Args:
            file_handle : SRT file handle
            inferred_text : text to be written
            line_count : subtitle line count
            limits : starting and ending times for text
        '''

        # TO-DO: Fix huge texts in long time to smooth it on screen while time pass
        # if self.check_if_should_break_text:
        #     text = self.adjust_text(text)

        start_at, end_at = [limit for limit in limits]

        from_dur = self.seconds_to_srt_timestamp(start_at)
        to_dur   = self.seconds_to_srt_timestamp(end_at)

        file_handle.write(f'{str(line_count)}\n')
        file_handle.write(f'{from_dur} --> {to_dur}\n')
        file_handle.write(f'{inferred_text}\n\n')

    def check_if_should_break_text(self, text, start_at, end_at):
        duration     = end_at - end_at
        min_duration = 10
        max_text_len = 20

        return True if duration > min_duration and len(text) > max_text_len else False

    def seconds_to_srt_timestamp(self, seconds):
        '''
        Convert seconds to 'HH:MM:SS.FFF' SRT format
        Args:
            seconds : time in seconds
        '''

        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)

        return '{:02.0f}:{:02.0f}:{:06.3f}'.format(h, m, s)

    def adjust_text(self, text):
        '''
        Wrap text to avoid very long texts
        Args:
            text : text of subtitle
        '''

        caracter_limit = 60
        return '\n'.join(wrap(text, caracter_limit))

def show_suported_languages(search_country=None):
    langs_dict = GoogleTranslator().get_supported_languages(as_dict=True)

    if search_country:
        if langs_dict[search_country] != None:
            print(search_country, '->', langs_dict[search_country])
        else:
            print('language not supported')
    else:
        for country, code in langs_dict.items():
            print(country, '->', code)
