"""Hardware detection and model configuration for JARVIS."""

import sys
from dataclasses import dataclass
from typing import Literal

import torch


@dataclass(frozen=True)
class ModelConfig:
    """Configuration for models based on hardware profile."""
    
    whisper_model: Literal["tiny", "small", "medium", "large-v3"]
    tts_engine: Literal["piper", "higgs"]
    llm_model: str
    device: Literal["cpu", "cuda"]


class HardwareDetector:
    """Detects hardware capabilities and returns appropriate model configuration."""
    
    VRAM_LOW_MIN = 6 * 1024**3
    VRAM_LOW_MAX = 8 * 1024**3
    VRAM_MID_MIN = 10 * 1024**3
    VRAM_MID_MAX = 16 * 1024**3
    VRAM_HIGH_MIN = 24 * 1024**3
    
    MODEL_PROFILES: dict[str, ModelConfig] = {
        "cpu": ModelConfig(
            whisper_model="tiny",
            tts_engine="piper",
            llm_model="phi3:mini",
            device="cpu"
        ),
        "low_gpu": ModelConfig(
            whisper_model="small",
            tts_engine="piper",
            llm_model="llama3.2:3b",
            device="cuda"
        ),
        "mid_gpu": ModelConfig(
            whisper_model="medium",
            tts_engine="higgs",
            llm_model="llama3.1:8b",
            device="cuda"
        ),
        "high_gpu": ModelConfig(
            whisper_model="large-v3",
            tts_engine="higgs",
            llm_model="llama3.1:70b",
            device="cuda"
        )
    }
    
    @classmethod
    def detect(cls) -> tuple[str, ModelConfig]:
        """Detect hardware and return profile name with model configuration."""
        if not torch.cuda.is_available():
            return "cpu", cls.MODEL_PROFILES["cpu"]
        
        try:
            device_props = torch.cuda.get_device_properties(0)
            vram_bytes = device_props.total_memory
            vram_gb = vram_bytes / (1024**3)
            
            if vram_bytes >= cls.VRAM_HIGH_MIN:
                profile = "high_gpu"
            elif cls.VRAM_MID_MIN <= vram_bytes <= cls.VRAM_MID_MAX:
                profile = "mid_gpu"
            elif cls.VRAM_LOW_MIN <= vram_bytes <= cls.VRAM_LOW_MAX:
                profile = "low_gpu"
            else:
                profile = "cpu"
            
            return profile, cls.MODEL_PROFILES[profile]
            
        except (RuntimeError, AttributeError):
            return "cpu", cls.MODEL_PROFILES["cpu"]
    
    @classmethod
    def print_startup_banner(cls, profile: str, config: ModelConfig) -> None:
        """Print startup banner with hardware and model information."""
        if torch.cuda.is_available():
            try:
                device_props = torch.cuda.get_device_properties(0)
                vram_gb = device_props.total_memory / (1024**3)
                gpu_name = device_props.name
            except (RuntimeError, AttributeError):
                gpu_name = "Unknown GPU"
                vram_gb = 0.0
            hardware_info = f"{gpu_name} ({vram_gb:.1f} GB VRAM)"
        else:
            hardware_info = "CPU Only"
        
        banner_lines = [
            "=" * 60,
            "                JARVIS VOICE ASSISTANT",
            "=" * 60,
            f"Hardware Profile: {profile.upper()}",
            f"Hardware: {hardware_info}",
            "-" * 60,
            "Model Configuration:",
            f"  STT Model:     faster-whisper ({config.whisper_model})",
            f"  TTS Engine:    {config.tts_engine}",
            f"  LLM Model:     {config.llm_model}",
            f"  Device:        {config.device}",
            "=" * 60,
        ]
        
        for line in banner_lines:
            print(line, file=sys.stdout)
        sys.stdout.flush()


def get_hardware_config() -> tuple[str, ModelConfig]:
    """Convenience function to detect hardware and print banner."""
    profile, config = HardwareDetector.detect()
    HardwareDetector.print_startup_banner(profile, config)
    return profile, config
