# Dictionnaire de mapping : Code Whisper (ISO-639-1) -> Code NLLB (FLORES-200)
WHISPER_TO_NLLB = {
    "en": "eng_Latn",
    "fr": "fra_Latn",
    "ar": "arb_Arab",
    "zh": "zho_Hans",
    "es": "spa_Latn",
    "de": "deu_Latn",
    "ru": "rus_Cyrl",
    "ja": "jpn_Jpan",
    "it": "ita_Latn",
    # Ajouter d'autres mappings si nécessaire
}

def get_nllb_code(whisper_code):
    """
    Retourne le code NLLB correspondant au code Whisper.
    Par défaut, retourne l'anglais si inconnu.
    """
    return WHISPER_TO_NLLB.get(whisper_code, "eng_Latn")