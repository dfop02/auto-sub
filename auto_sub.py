import os
import time
import datetime
import speech_recognition as sr
import moviepy.editor as mp
from pydub import AudioSegment
from split_on_silence_with_timing import split_on_silence_with_timing
from deep_translator import GoogleTranslator
from pathlib import Path

class AutoSub:
    video_name = None
    audio      = None
    from_lang  = None
    to_lang    = None
    verbose    = True

    def __init__(self, video_path, from_lang='ja', to_lang='pt'):
        self.video_name = Path(video_path).stem
        self.audio      = self.get_audio_from_video(video_path)
        self.from_lang  = from_lang
        self.to_lang    = to_lang

    def show_suported_languages(self):
        langs_dict = GoogleTranslator().get_supported_languages(as_dict=True)
        for country, code in langs_dict:
            print(country, '->', code)

    def get_audio_from_video(self, video):
        # open video as a file
        clip = mp.VideoFileClip(video)
        # Set audio path
        audio_path = "tmp/{}.wav".format(self.video_name)
        # Remove audio from video and save as a wav file
        clip.audio.write_audiofile(audio_path)
        # open the audio file stored in the local system as a wav file.
        return AudioSegment.from_wav(audio_path)

    # a function that splits the audio file into chunks
    # and applies speech recognition for create subtitles
    def generate_subtitles(self):
        # open a file where we will concatenate and store the subtitle text
        fh = open("tmp/{}.srt".format(self.video_name), "w+")

        print("Creating chunks...") if self.verbose else None
        start = time.perf_counter() if self.verbose else None

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

        print(f"Completed chunks creation in {time.perf_counter() - start} seconds") if self.verbose else None

        # create a directory to store the audio chunks.
        os.makedirs('tmp/audio_chunks', exist_ok=True)

        # create a speech recognition object
        recognizer = sr.Recognizer()

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
                # remove ambient noise
                # recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_listened = rrecognizer.listen(source)

            try:
                # try converting it to text
                rec    = recognizer.recognize_google(audio_listened, language="ja-JP")
                rec_pt = self.jap_to_pt(rec)
                text   = rec_pt if rec_pt else rec
                print("  " + text) if self.verbose else None
                self.write_to_file(fh, text, line_count, (start_clip, end_clip))
                valid_recognize+=1
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
        translated_text = None

        try:
            translated_text = GoogleTranslator(source=self.from_lang, target=self.to_lang).translate(text=text)
        except Exception as e:
            print(str(e))

        return translated_text

    def write_to_file(self, file_handle, inferred_text, line_count, limits):
        """Write the inferred text to SRT file
        Follows a specific format for SRT files
        Args:
            file_handle : SRT file handle
            inferred_text : text to be written
            line_count : subtitle line count
            limits : starting and ending times for text
        """

        d = str(datetime.timedelta(seconds=float(limits[0])))
        try:
            from_dur = "0" + str(d.split(".")[0]) + "," + str(d.split(".")[-1][:2])
        except:
            from_dur = "0" + str(d) + "," + "00"

        d = str(datetime.timedelta(seconds=float(limits[1])))
        try:
            to_dur = "0" + str(d.split(".")[0]) + "," + str(d.split(".")[-1][:2])
        except:
            to_dur = "0" + str(d) + "," + "00"

        file_handle.write(str(line_count) + "\n")
        file_handle.write(from_dur + " --> " + to_dur + "\n")
        file_handle.write(inferred_text + "\n\n")
