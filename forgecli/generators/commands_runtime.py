"""Runtime mirror of the generated tool's command registry.

This module lets ForgeCLI itself (e.g. the README generator) look up the
*names* of commands that a generated tool will expose, without importing the
templated ``commands.py`` source. Keep this in sync with
``templates/commands.py.tpl`` - same categories/subcategories and command
labels.
"""
from __future__ import annotations

from typing import List, Tuple

Command = Tuple[str, None]

COMMANDS: dict[str, dict[str, List[str]]] = {
    "Cybersecurity": {
        "Port Scanner": ["TCP connect scan"],
        "DNS": ["Lookup A/AAAA"],
        "WHOIS": ["Lookup"],
        "Hash Tool": ["Compute hash"],
        "Encryption": ["Symmetric encrypt/decrypt"],
        "Encoding": ["Encoder/Decoder"],
        "Reverse Shell Helper": ["One-liner generator"],
        "Payload Generator": ["msfvenom template"],
        "Web Scanner": ["HTTP header check"],
        "Recon": ["Domain recon"],
        "Network Monitor": ["/proc/net/dev sampler"],
        "Log Analyzer": ["Count by level"],
        "CTF Tool": ["Encoder toolbox"],
        "Custom": ["OSINT username search", "WiFi scan", "Bluetooth scan",
                    "Packet analyzer"],
    },
    "Networking": {
        "Port Scanner": ["TCP connect scan"],
        "DNS": ["Lookup A/AAAA"],
        "Ping Sweep": ["CIDR ping sweep"],
        "Traceroute": ["Run traceroute"],
        "Bandwidth Monitor": ["Download speed test"],
        "Port Forwarder": ["TCP forwarder"],
        "DNS Lookup": ["Lookup A/AAAA"],
        "Custom": ["Domain recon"],
    },
    "Developer": {
        "Code Generator": ["Snippet manager"],
        "Boilerplate": ["Snippet manager"],
        "Git Helper": ["System info"],
        "Regex Tester": ["Run regex"],
        "Snippet Manager": ["Manage snippets"],
        "Custom": ["Regex tester"],
    },
    "Automation": {
        "Task Runner": ["Todo list"],
        "File Batch": ["System info"],
        "Web Scraper": ["Scrape links"],
        "Scheduler": ["Timer"],
        "Custom": ["Todo"],
    },
    "API": {
        "REST Client": ["REST request"],
        "GraphQL Client": ["REST request (fallback)"],
        "Webhook Server": ["Run webhook server"],
        "Mock Server": ["Run webhook server (mock)"],
        "Custom": ["REST request"],
    },
    "OSINT": {
        "Username Lookup": ["Cross-site search"],
        "Email Recon": ["Resolve & WHOIS"],
        "Domain Recon": ["DNS + robots + security.txt"],
        "Social Scan": ["Cross-site search"],
        "Custom": ["Domain recon"],
    },
    "Bluetooth": {
        "Device Scan": ["hcitool/bluetoothctl scan"],
        "BLE Tool": ["Bluetooth scan"],
        "GATT Explorer": ["Bluetooth scan"],
        "Custom": ["Bluetooth scan"],
    },
    "WiFi": {
        "Network Scan": ["nmcli/iwlist scan"],
        "Handshake Capture Helper": ["WiFi scan"],
        "Signal Mapper": ["WiFi scan"],
        "Custom": ["WiFi scan"],
    },
    "RF": {
        "SDR Helper": ["System info"],
        "Frequency Scanner": ["System info"],
        "Custom": ["System info"],
    },
    "Hardware": {
        "Serial Monitor": ["List serial ports"],
        "Flasher": ["System info"],
        "Sensor Reader": ["System info"],
        "Custom": ["Serial monitor"],
    },
    "ESP32": {
        "Firmware Flasher": ["Serial monitor"],
        "OTA Helper": ["Serial monitor"],
        "MQTT Bridge": ["IoT discovery"],
        "Custom": ["Serial monitor"],
    },
    "Arduino": {
        "Sketch Builder": ["Snippet manager"],
        "Serial Console": ["Serial monitor"],
        "Custom": ["Serial monitor"],
    },
    "IoT": {
        "Device Discovery": ["mDNS browse"],
        "MQTT Client": ["mDNS browse"],
        "Telemetry Viewer": ["System info"],
        "Custom": ["mDNS browse"],
    },
    "CLI Utility": {
        "Calculator": ["Evaluate expression"],
        "Unit Converter": ["Convert units"],
        "Password Gen": ["Generate password"],
        "Color Tool": ["Convert colors"],
        "Custom": ["Calculator", "Color tool"],
    },
    "AI": {
        "Prompt Runner": ["REST request (LLM endpoint)"],
        "LLM Client": ["REST request (LLM endpoint)"],
        "Vector Search": ["Regex search local snippets"],
        "Custom": ["REST request"],
    },
    "Machine Learning": {
        "Dataset Cleaner": ["Snippet manager (jsonl)"],
        "Model Trainer": ["System info"],
        "Eval Tool": ["REST request"],
        "Custom": ["REST request"],
    },
    "Forensics": {
        "Disk Image": ["Hash file"],
        "Memory Dump": ["Hash file"],
        "Timeline Builder": ["Log analyzer"],
        "Custom": ["Hash file"],
    },
    "Password Tools": {
        "Generator": ["Generate password"],
        "Strength Meter": ["Measure entropy"],
        "Hash Cracker Helper": ["Compute hash"],
        "Vault": ["Snippet manager"],
        "Custom": ["Password generator"],
    },
    "Monitoring": {
        "System Watcher": ["Network sampler"],
        "Log Tail": ["Log analyzer"],
        "Uptime Pinger": ["Ping sweep"],
        "Custom": ["Network monitor"],
    },
    "Discord": {
        "Bot Template": ["REST request (Discord API)"],
        "Webhook Sender": ["REST request (Discord API)"],
        "Message Logger": ["Webhook server"],
        "Custom": ["REST request"],
    },
    "Telegram": {
        "Bot Template": ["REST request (Telegram API)"],
        "Channel Poster": ["REST request (Telegram API)"],
        "Custom": ["REST request"],
    },
    "WhatsApp": {
        "Web Client": ["REST request"],
        "Auto Reply": ["Webhook server"],
        "Custom": ["REST request"],
    },
    "Crypto": {
        "Price Tracker": ["Fetch live price"],
        "Wallet Tool": ["Hash helper"],
        "Transaction Decoder": ["Hex decode"],
        "Custom": ["Price tracker"],
    },
    "Productivity": {
        "Todo": ["Todo list"],
        "Notes": ["Snippet manager"],
        "Timer": ["Countdown"],
        "Kanban": ["Todo list"],
        "Custom": ["Todo"],
    },
    "Custom": {
        "Custom": ["System info", "Help"],
    },
}


def commands_for(category: str, subcategory: str) -> List[Command]:
    bucket = COMMANDS.get(category, {})
    names = bucket.get(subcategory, bucket.get("Custom", []))
    return [(name, None) for name in names]


__all__ = ["COMMANDS", "commands_for"]