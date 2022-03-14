from pydub.silence import detect_nonsilent, split_on_silence

def split_on_silence_with_timing(audio_segment, min_silence_len=1000, silence_thresh=-16, keep_silence=100,
                                 seek_step=1, with_timing=True):
    """
    audio_segment - original pydub.AudioSegment() object
    min_silence_len - (in ms) minimum length of a silence to be used for
        a split. default: 1000ms
    silence_thresh - (in dBFS) anything quieter than this will be
        considered silence. default: -16dBFS
    keep_silence - (in ms) amount of silence to leave at the beginning
        and end of the chunks. Keeps the sound from sounding like it is
        abruptly cut off. (default: 100ms)
    with_timing - return timestamp in ms with each chunk (start, end, chunk)
    """

    not_silence_ranges = detect_nonsilent(audio_segment, min_silence_len, silence_thresh, seek_step)

    chunks = []
    if with_timing:
        for start_i, end_i in not_silence_ranges:
            start_i = max(0, start_i - keep_silence)
            end_i += keep_silence
            chunks.append((int(start_i / 1000), (int(end_i / 1000)), audio_segment[start_i:end_i]))
    else:
        for start_i, end_i in not_silence_ranges:
            start_i = max(0, start_i - keep_silence)
            end_i += keep_silence
            chunks.append(audio_segment[start_i:end_i])

    return chunks
