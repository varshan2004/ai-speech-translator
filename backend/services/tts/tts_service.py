import edge_tts
import asyncio
import uuid
import os

# ALWAYS resolve absolute path
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

OUTPUT_DIR = os.path.join(BASE_DIR, "temp_audio")
os.makedirs(OUTPUT_DIR, exist_ok=True)

VOICE_MAP = {
    "en": "en-IN-NeerjaNeural",
    "hi": "hi-IN-MadhurNeural",
    "ta": "ta-IN-PallaviNeural",
    "te": "te-IN-ShrutiNeural",
    "ml": "ml-IN-SobhanaNeural",
    "kn": "kn-IN-GaganNeural",
    "bn": "bn-IN-TanishaaNeural",
    "gu": "gu-IN-DhwaniNeural",
    "mr": "mr-IN-AarohiNeural",
    "pa": "pa-IN-VaaniNeural",
    "ur": "ur-IN-GulNeural",
    "or": "or-IN-SukritiNeural",
    "as": "as-IN-YashicaNeural"
}

async def _synthesize_async(text: str, lang: str) -> str:
    voice = VOICE_MAP.get(lang, VOICE_MAP["en"])

    filename = f"{uuid.uuid4()}.mp3"
    output_path = os.path.join(OUTPUT_DIR, filename)

    tts = edge_tts.Communicate(text=text, voice=voice)
    await tts.save(output_path)

    return output_path  # FULL PATH

def synthesize(text: str, lang: str) -> str:
    return asyncio.run(_synthesize_async(text, lang))
