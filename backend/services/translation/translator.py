import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODEL_NAME = "facebook/nllb-200-distilled-600M"

LANG_CODE_MAP = {
    "en": "eng_Latn",
    "hi": "hin_Deva",
    "ta": "tam_Taml",
    "te": "tel_Telu",
    "ml": "mal_Mlym",
    "kn": "kan_Knda",
    "bn": "ben_Beng",
    "gu": "guj_Gujr",
    "mr": "mar_Deva",
    "pa": "pan_Guru",
    "ur": "urd_Arab",
    "or": "ory_Orya",
    "as": "asm_Beng"
}

class Translator:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
        self.model.to(self.device)
        self.model.eval()

    def translate(self, text: str, target_lang: str) -> str:
        if target_lang not in LANG_CODE_MAP:
            raise ValueError(f"Unsupported target language: {target_lang}")

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True
        ).to(self.device)

        target_token_id = self.tokenizer.convert_tokens_to_ids(
            LANG_CODE_MAP[target_lang]
        )

        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                forced_bos_token_id=target_token_id,
                max_length=256
            )

        translated_text = self.tokenizer.decode(
            output[0],
            skip_special_tokens=True
        )

        return translated_text.strip()
