"""
Audio endpoints — GET /audio/{filename}, GET /list-audio, DELETE /audio/{filename}.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.core.config import Settings
from app.core.dependencies import get_app_settings
from app.services.audio_service import get_audio_path, list_audio, delete_audio

router = APIRouter(tags=["audio"])


@router.get("/audio/{filename}")
async def get_audio(
    filename: str,
    settings: Settings = Depends(get_app_settings),
):
    """Download a generated audio file."""
    audio_path = get_audio_path(filename, settings.AUDIO_DIR)
    if audio_path is None:
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(audio_path, media_type="audio/wav", filename=filename)


@router.get("/list-audio")
async def list_audio_files(settings: Settings = Depends(get_app_settings)):
    """List all generated audio files."""
    files = list_audio(settings.AUDIO_DIR)
    return {"audio_files": files, "count": len(files)}


@router.delete("/audio/{filename}")
async def delete_audio_file(
    filename: str,
    settings: Settings = Depends(get_app_settings),
):
    """Delete a specific audio file."""
    try:
        delete_audio(filename, settings.AUDIO_DIR)
        return {"status": "success", "message": f"Deleted {filename}"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Audio file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")
