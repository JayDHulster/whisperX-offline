# Predownload all alignment models by running this file seperately

import os
import torchaudio
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from transformers.utils import cached_file
from tqdm import tqdm

DEFAULT_ALIGN_MODELS_TORCH = {
    "en": "WAV2VEC2_ASR_BASE_960H",
    "fr": "VOXPOPULI_ASR_BASE_10K_FR",
    "de": "VOXPOPULI_ASR_BASE_10K_DE",
    "es": "VOXPOPULI_ASR_BASE_10K_ES",
    "it": "VOXPOPULI_ASR_BASE_10K_IT",
}

DEFAULT_ALIGN_MODELS_HF = {
    "ja": "jonatasgrosman/wav2vec2-large-xlsr-53-japanese",
    "zh": "jonatasgrosman/wav2vec2-large-xlsr-53-chinese-zh-cn",
    "nl": "jonatasgrosman/wav2vec2-large-xlsr-53-dutch",
    "uk": "Yehor/wav2vec2-xls-r-300m-uk-with-small-lm",
    "pt": "jonatasgrosman/wav2vec2-large-xlsr-53-portuguese",
    "ar": "jonatasgrosman/wav2vec2-large-xlsr-53-arabic",
    "cs": "comodoro/wav2vec2-xls-r-300m-cs-250",
    "ru": "jonatasgrosman/wav2vec2-large-xlsr-53-russian",
    "pl": "jonatasgrosman/wav2vec2-large-xlsr-53-polish",
    "hu": "jonatasgrosman/wav2vec2-large-xlsr-53-hungarian",
    "fi": "jonatasgrosman/wav2vec2-large-xlsr-53-finnish",
    "fa": "jonatasgrosman/wav2vec2-large-xlsr-53-persian",
    "el": "jonatasgrosman/wav2vec2-large-xlsr-53-greek",
    "tr": "mpoyraz/wav2vec2-xls-r-300m-cv7-turkish",
    "da": "saattrupdan/wav2vec2-xls-r-300m-ftspeech",
    "he": "imvladikon/wav2vec2-xls-r-300m-hebrew",
    "vi": "nguyenvulebinh/wav2vec2-base-vi",
    "ko": "kresnik/wav2vec2-large-xlsr-korean",
    "ur": "kingabzpro/wav2vec2-large-xls-r-300m-Urdu",
    "te": "anuragshas/wav2vec2-large-xlsr-53-telugu",
    "hi": "theainerd/Wav2Vec2-large-xlsr-hindi",
    "ca": "softcatala/wav2vec2-large-xlsr-catala",
    "ml": "gvs/wav2vec2-large-xlsr-malayalam",
    "no": "NbAiLab/nb-wav2vec2-1b-bokmaal-v2",
    "nn": "NbAiLab/nb-wav2vec2-1b-nynorsk",
    "sk": "comodoro/wav2vec2-xls-r-300m-sk-cv8",
    "sl": "anton-l/wav2vec2-large-xlsr-53-slovenian",
    "hr": "classla/wav2vec2-xls-r-parlaspeech-hr",
    "ro": "gigant/romanian-wav2vec2",
    "eu": "stefan-it/wav2vec2-large-xlsr-53-basque",
    "gl": "ifrz/wav2vec2-large-xlsr-galician",
    "ka": "xsway/wav2vec2-large-xlsr-georgian",
    "lv": "jimregan/wav2vec2-large-xlsr-latvian-cv",
    "tl": "Khalsuu/filipino-wav2vec2-l-xls-r-300m-official",
}

MODEL_DIR = "./models"
os.makedirs(MODEL_DIR, exist_ok=True)

def download_torchaudio_models():
    for lang, model_name in tqdm(DEFAULT_ALIGN_MODELS_TORCH.items(), desc="Torchaudio models"):
        bundle = torchaudio.pipelines.__dict__[model_name]
        # This will skip if already cached
        _ = bundle.get_model(dl_kwargs={"model_dir": MODEL_DIR})

def download_hf_models():
    for lang, model_name in tqdm(DEFAULT_ALIGN_MODELS_HF.items(), desc="HF models"):
        try:
            # Check if already cached
            _ = cached_file(model_name, "pytorch_model.bin", cache_dir=MODEL_DIR, local_files_only=True)
            print(f"✔ {model_name} already cached, skipping")
            continue
        except EnvironmentError:
            pass  # Not cached yet, so download

        print(f"⬇ Downloading {model_name}")
        _ = Wav2Vec2Processor.from_pretrained(model_name, cache_dir=MODEL_DIR)
        _ = Wav2Vec2ForCTC.from_pretrained(model_name, cache_dir=MODEL_DIR)

if __name__ == "__main__":
    download_torchaudio_models()
    download_hf_models()
    print("✅ All models are now cached in", MODEL_DIR)
