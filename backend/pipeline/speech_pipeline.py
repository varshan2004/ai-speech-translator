import os
import re
import uuid
from pydub import AudioSegment

from backend.services.asr.whisper_service import WhisperASR
from backend.services.translation.translator import Translator
from backend.services.tts.tts_service import synthesize


class SpeechPipeline:
    def __init__(self):
        self.asr = WhisperASR()
        self.translator = Translator()

    def _split_text(self, text, max_chars=300):
        """
        Split long text into TTS-safe chunks
        """
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current = ""

        for s in sentences:
            if len(current) + len(s) <= max_chars:
                current += " " + s
            else:
                chunks.append(current.strip())
                current = s

        if current.strip():
            chunks.append(current.strip())

        return chunks

    def process_audio(self, audio_path: str, target_lang: str):
        # 1. ASR (FULL LENGTH)
        original_text, captions = self.asr.transcribe_with_timestamps(audio_path)

        # 2. TRANSLATION (FULL TEXT)
        translated_text = self.translator.translate(
            original_text,
            target_lang
        )

        # 3. TTS CHUNKING (CRITICAL FIX)
        text_chunks = self._split_text(translated_text)

        audio_segments = []
        temp_files = []

        for chunk in text_chunks:
            audio_chunk_path = synthesize(chunk, target_lang)
            temp_files.append(audio_chunk_path)

            audio_segments.append(
                AudioSegment.from_file(audio_chunk_path)
            )

        # 4. MERGE AUDIO
        final_audio = AudioSegment.empty()
        for seg in audio_segments:
            final_audio += seg

        final_filename = f"{uuid.uuid4()}.mp3"
        final_path = os.path.join(
            os.path.dirname(temp_files[0]),
            final_filename
        )

        final_audio.export(final_path, format="mp3")

        # Optional: cleanup temp chunk files
        for f in temp_files:
            try:
                os.remove(f)
            except Exception:
                pass

        return {
            "original_text": original_text,
            "translated_text": translated_text,
            "audio_path": os.path.basename(final_path),
            "captions": captions
        }
