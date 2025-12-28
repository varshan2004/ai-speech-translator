import torch
import librosa
import numpy as np
from transformers import WhisperProcessor, WhisperForConditionalGeneration

MODEL_PATH = "models/whisper_tiny_stage2"

CHUNK_LENGTH = 30  # seconds (Whisper safe window)
SAMPLE_RATE = 16000


class WhisperASR:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.processor = WhisperProcessor.from_pretrained(MODEL_PATH)
        self.model = WhisperForConditionalGeneration.from_pretrained(MODEL_PATH)
        self.model.to(self.device)
        self.model.eval()

    def transcribe_with_timestamps(self, audio_path: str):
        # Load full audio
        audio, _ = librosa.load(audio_path, sr=SAMPLE_RATE)

        chunk_size = CHUNK_LENGTH * SAMPLE_RATE
        total_length = len(audio)

        full_text_parts = []
        captions = []

        chunk_index = 0

        for start in range(0, total_length, chunk_size):
            end = start + chunk_size
            audio_chunk = audio[start:end]

            if len(audio_chunk) < SAMPLE_RATE:  # skip tiny tail
                continue

            inputs = self.processor(
                audio_chunk,
                sampling_rate=SAMPLE_RATE,
                return_tensors="pt"
            )

            with torch.no_grad():
                output = self.model.generate(
                    inputs.input_features.to(self.device),
                    return_timestamps=True,
                    max_new_tokens=440
                )

            # Decode text
            text = self.processor.batch_decode(
                output,
                skip_special_tokens=True
            )[0].strip()

            if text:
                full_text_parts.append(text)

            # Decode timestamps
            segments = self.processor.tokenizer._decode_with_timestamps(
                output[0].tolist()
            )

            time_offset = chunk_index * CHUNK_LENGTH

            for seg in segments:
                if isinstance(seg, dict) and "text" in seg:
                    captions.append({
                        "start": round(seg["start"] + time_offset, 2),
                        "end": round(seg["end"] + time_offset, 2),
                        "text": seg["text"].strip()
                    })

            chunk_index += 1

        full_text = " ".join(full_text_parts)

        return full_text.strip(), captions
