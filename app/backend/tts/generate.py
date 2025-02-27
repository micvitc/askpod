import soundfile as sf
import numpy as np
from kokoro import KPipeline
import soundfile as sf
import os

pipeline = KPipeline(lang_code="a")


def generate_audio_sentence(text, voice):
    audio_segments = []
    if voice == "female_section":
        for i, (gs, ps, audio) in enumerate(
            pipeline(text, voice="af_heart", speed=1, split_pattern=r"\n+")
        ):
            audio_segments.append(audio)
    else:
        for i, (gs, ps, audio) in enumerate(
            pipeline(text, voice="am_adam", speed=1, split_pattern=r"\n+")
        ):
            audio_segments.append(audio)

    return audio_segments


def generate_audio(transcript, output_filename="combined_audio.wav"):
    audio_segments = []

    for t in transcript:
        for gender, sent in t.items():
            if gender == "male_section":
                audio_segments.extend(generate_audio_sentence(sent, "male_section"))
            else:
                audio_segments.extend(generate_audio_sentence(sent, "female_section"))

    combined_audio = np.concatenate(audio_segments)
    output_filename = os.path.join(output_filename)
    sf.write(output_filename, combined_audio, 24000)


# def generate_audio(text, output_filename="combined_audio.wav"):
#     audio_segments = []
#     for i, (gs, ps, audio) in enumerate(
#         pipeline(text, voice="af_heart", speed=1, split_pattern=r"\n+")
#     ):
#         audio_segments.append(audio)

#     combined_audio = np.concatenate(audio_segments)
#     output_filename = os.path.join(output_filename)
#     sf.write(output_filename, combined_audio, 24000)
