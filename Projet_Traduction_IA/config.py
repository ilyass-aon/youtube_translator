import os
import torch

# --- DETECTION DU MATERIEL ---
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f" Configuration : Exécution sur {DEVICE.upper()}")

# --- MODELES ---
MODEL_WHISPER = "base"  # "tiny", "base", "small", "medium", "large"
MODEL_TRANSLATOR = "facebook/nllb-200-distilled-600M"

# --- CHEMINS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

# Création automatique du dossier output
os.makedirs(OUTPUT_DIR, exist_ok=True)