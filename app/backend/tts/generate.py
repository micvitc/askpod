import soundfile as sf
import numpy as np
from kokoro import KPipeline
import soundfile as sf
import os

pipeline = KPipeline(lang_code="a")


def generate_audio(text, output_filename="combined_audio.wav"):
    os.makedirs("audio", exist_ok=True)
    audio_segments = []
    for i, (gs, ps, audio) in enumerate(
        pipeline(text, voice="af_heart", speed=1, split_pattern=r"\n+")
    ):
        audio_segments.append(audio)

    combined_audio = np.concatenate(audio_segments)
    output_filename = os.path.join("audio", output_filename)
    sf.write(output_filename, combined_audio, 24000)
