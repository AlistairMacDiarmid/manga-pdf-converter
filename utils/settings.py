import json
import os

SETTINGS_FILE = "settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load settings: {e}")
    #return default settings if file doesn't exist or error
    return {
        'pdf_quality': 85,
        'image_processing': 'keep_original',
        'pdf_compression': True,
        'resize_images': False,
        'max_width': 1920,
        'max_height': 1080,
        'output_folder': '',
        'auto_open_pdf': False,
        'backup_originals': False,
        'delete_after_conversion': False,
        'theme': 'dark'
    }

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Failed to save settings: {e}")
