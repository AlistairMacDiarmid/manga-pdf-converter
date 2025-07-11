import os

def load_stylesheet(name):
    base_path = os.path.join(os.path.dirname(__file__), '..', 'styles')
    path = os.path.join(base_path, f"{name}.qss")
    try:
        with open(path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return ""