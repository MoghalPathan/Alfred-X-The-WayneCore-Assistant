"""
AlfredX: TTS compatibility shim.
The project had two TTS engines (tts.py and tts_engine.py) which could
drift apart and cause "sometimes silent" bugs. tts_engine.py is now the
single source of truth; this file re-exports it so any code importing
core.tts keeps working.
"""
from core.tts_engine import TTSEngine  # noqa: F401