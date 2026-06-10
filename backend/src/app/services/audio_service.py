"""
Audio service — TTS generation and audio file management.

Extracted from app.py. The save_audio() core logic is identical;
helper functions are extracted from the audio route handlers.
"""

import os
from datetime import datetime

import pyttsx3


def save_audio(text: str, audio_dir: str) -> str:
    """Save text as audio file using local TTS engine.

    Args:
        text: The text to convert to speech.
        audio_dir: Directory to save the audio file in.

    Returns:
        Full path to the saved audio file.
    """
    engine = pyttsx3.init()
    engine.setProperty("rate", 170)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_path = os.path.join(audio_dir, f"response_{timestamp}.wav")

    engine.save_to_file(text, audio_path)
    engine.runAndWait()
    engine.stop()

    return audio_path


def get_audio_path(filename: str, audio_dir: str) -> str | None:
    """Resolve an audio filename to its full path, or None if not found."""
    audio_path = os.path.join(audio_dir, filename)
    if os.path.exists(audio_path):
        return audio_path
    return None


def list_audio(audio_dir: str) -> list[str]:
    """List all .wav audio files in the audio directory, newest first."""
    if not os.path.exists(audio_dir):
        return []
    files = [f for f in os.listdir(audio_dir) if f.endswith(".wav")]
    files.sort(reverse=True)
    return files


def delete_audio(filename: str, audio_dir: str) -> bool:
    """Delete a specific audio file. Returns True on success.

    Raises:
        FileNotFoundError: If the file does not exist.
        OSError: If the file cannot be deleted.
    """
    audio_path = os.path.join(audio_dir, filename)
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {filename}")
    os.remove(audio_path)
    return True
