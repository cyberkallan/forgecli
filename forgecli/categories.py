"""Tool categories and subcategories offered by ForgeCLI."""
from __future__ import annotations

from typing import Dict, List


# Each top-level category maps to a list of subcategories. ``Custom`` is always
# appended so users can build free-form tools.
TOOL_CATEGORIES: Dict[str, List[str]] = {
    "Cybersecurity": [
        "Port Scanner", "Information Gathering", "DNS", "WHOIS", "OSINT",
        "WiFi Scanner", "Bluetooth Scanner", "Packet Analyzer", "Hash Tool",
        "Encryption", "Encoding", "Reverse Shell Helper", "Payload Generator",
        "Web Scanner", "Recon", "Network Monitor", "Log Analyzer", "CTF Tool",
        "Custom",
    ],
    "Networking": ["Ping Sweep", "Traceroute", "Bandwidth Monitor", "Port Forwarder", "DNS Lookup", "Custom"],
    "Developer": ["Code Generator", "Boilerplate", "Git Helper", "Regex Tester", "Snippet Manager", "Custom"],
    "Automation": ["Task Runner", "File Batch", "Web Scraper", "Scheduler", "Custom"],
    "API": ["REST Client", "GraphQL Client", "Webhook Server", "Mock Server", "Custom"],
    "OSINT": ["Username Lookup", "Email Recon", "Domain Recon", "Social Scan", "Custom"],
    "Bluetooth": ["Device Scan", "BLE Tool", "GATT Explorer", "Custom"],
    "WiFi": ["Network Scan", "Handshake Capture Helper", "Signal Mapper", "Custom"],
    "RF": ["SDR Helper", "Frequency Scanner", "Custom"],
    "Hardware": ["Serial Monitor", "Flasher", "Sensor Reader", "Custom"],
    "ESP32": ["Firmware Flasher", "OTA Helper", "MQTT Bridge", "Custom"],
    "Arduino": ["Sketch Builder", "Serial Console", "Custom"],
    "IoT": ["Device Discovery", "MQTT Client", "Telemetry Viewer", "Custom"],
    "CLI Utility": ["Calculator", "Unit Converter", "Password Gen", "Color Tool", "Custom"],
    "AI": ["Prompt Runner", "LLM Client", "Vector Search", "Custom"],
    "Machine Learning": ["Dataset Cleaner", "Model Trainer", "Eval Tool", "Custom"],
    "Forensics": ["Disk Image", "Memory Dump", "Timeline Builder", "Custom"],
    "Password Tools": ["Generator", "Strength Meter", "Hash Cracker Helper", "Vault", "Custom"],
    "Monitoring": ["System Watcher", "Log Tail", "Uptime Pinger", "Custom"],
    "Discord": ["Bot Template", "Webhook Sender", "Message Logger", "Custom"],
    "Telegram": ["Bot Template", "Channel Poster", "Custom"],
    "WhatsApp": ["Web Client", "Auto Reply", "Custom"],
    "Crypto": ["Price Tracker", "Wallet Tool", "Transaction Decoder", "Custom"],
    "Productivity": ["Todo", "Notes", "Timer", "Kanban", "Custom"],
    "Custom": ["Custom"],
}


def list_categories() -> List[str]:
    """Return category names."""
    return list(TOOL_CATEGORIES.keys())


def subcategories_for(category: str) -> List[str]:
    """Return subcategories for a category (empty list if unknown)."""
    return TOOL_CATEGORIES.get(category, ["Custom"])


def suggest_entrypoint(subcategory: str) -> str:
    """Suggest a CLI entrypoint name from a subcategory."""
    slug = subcategory.lower()
    for ch in " -":
        slug = slug.replace(ch, "_")
    return slug


__all__ = ["TOOL_CATEGORIES", "list_categories", "subcategories_for", "suggest_entrypoint"]