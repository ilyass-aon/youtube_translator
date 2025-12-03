from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch
import re
from config import MODEL_TRANSLATOR, DEVICE
from utils.lang_mapping import get_nllb_code

class UniversalTranslator:
    def __init__(self):
        
        print(f"[Translator] Chargement du modèle '{MODEL_TRANSLATOR}'...")
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_TRANSLATOR)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_TRANSLATOR).to(DEVICE)
        self.translator_pipeline = pipeline(
            "translation", 
            model=self.model, 
            tokenizer=self.tokenizer, 
            device=0 if DEVICE == "cuda" else -1,
            max_length=512
        )

    def _smart_chunking(self, text, max_chars=400):
        
        sentences = re.split(r'(?<=[.!?。！？])\s*', text)
        chunks = []
        current_chunk = ""
        for sentence in sentences:
            if not sentence.strip(): continue
            if len(current_chunk) + len(sentence) < max_chars:
                current_chunk += sentence + " "
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        if current_chunk: chunks.append(current_chunk.strip())
        return chunks

    def translate(self, text, source_lang_whisper, target_lang_whisper="fr", progress_callback=None):
        
        src_code_nllb = get_nllb_code(source_lang_whisper)
        tgt_code_nllb = get_nllb_code(target_lang_whisper)

        if src_code_nllb == tgt_code_nllb:
            if progress_callback: progress_callback(1.0) # 100% direct
            return text

        chunks = self._smart_chunking(text)
        translated_text = []
        
        total_chunks = len(chunks)

        for i, chunk in enumerate(chunks):
            try:
                result = self.translator_pipeline(chunk, src_lang=src_code_nllb, tgt_lang=tgt_code_nllb)
                translated_text.append(result[0]['translation_text'])
            except Exception:
                translated_text.append(chunk)

            # --- MISE A JOUR DE LA BARRE DE PROGRESSION ---
            if progress_callback:
                
                percent = (i + 1) / total_chunks
                progress_callback(percent)
                
        return " ".join(translated_text)