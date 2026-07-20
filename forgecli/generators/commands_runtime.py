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
        "Port Scanner": ["TCP connect scan", "Subnet calculator", "SSL/TLS cert scan",
                         "ARP scan (local)", "HTTP methods probe", "Headers dump"],
        "DNS": ["Lookup A/AAAA", "Reverse DNS", "SPF / DMARC"],
        "WHOIS": ["Lookup"],
        "Hash Tool": ["Compute hash", "Dictionary cracker", "Hash a file", "HMAC"],
        "Encryption": ["Symmetric encrypt/decrypt"],
        "Encoding": ["Encoder/Decoder", "Base58"],
        "Reverse Shell Helper": ["One-liner generator"],
        "Payload Generator": ["msfvenom template"],
        "Web Scanner": ["HTTP header check", "Directory buster", "JWT decode",
                        "robots.txt parser", "Sitemap parser", "URL unshortener"],
        "Recon": ["Domain recon", "Wayback Machine lookup",
                  "Certificate Transparency (crt.sh)", "GitHub user"],
        "Network Monitor": ["/proc/net/dev sampler", "Headers dump"],
        "Log Analyzer": ["Count by level"],
        "CTF Tool": ["Encoder toolbox", "All Caesar shifts (ROT)", "Vigenere cipher",
                     "Morse code", "JSON pretty / minify", "Hexdump", "Diff two strings"],
        "Custom": ["OSINT username search", "WiFi scan", "Bluetooth scan",
                   "Packet analyzer", "MAC vendor lookup"],
    },
    "Networking": {
        "Port Scanner": ["TCP connect scan", "Subnet calculator", "ARP scan",
                         "HTTP methods probe"],
        "DNS": ["Lookup A/AAAA", "Reverse DNS", "SPF / DMARC"],
        "Ping Sweep": ["CIDR ping sweep"],
        "Traceroute": ["Run traceroute"],
        "Bandwidth Monitor": ["Download speed test"],
        "Port Forwarder": ["TCP forwarder"],
        "DNS Lookup": ["Lookup A/AAAA"],
        "Custom": ["Domain recon", "Headers dump"],
    },
    "Developer": {
        "Code Generator": ["Snippet manager"],
        "Boilerplate": ["Snippet manager"],
        "Git Helper": ["GitHub user info", "List GitHub repos", "System info"],
        "Regex Tester": ["Run regex"],
        "Snippet Manager": ["Manage snippets"],
        "UUID Tool": ["Generate / parse UUID"],
        "Timestamp": ["Unix <> ISO"],
        "Custom": ["JSON pretty / minify", "TOML viewer"],
    },
    "Automation": {
        "Task Runner": ["Todo list"],
        "File Batch": ["Hexdump a file", "Hash a file", "Inspect zip"],
        "Web Scraper": ["Scrape links", "Sitemap parser", "robots.txt parser"],
        "Scheduler": ["Timer", "Cron builder"],
        "Custom": ["Todo list"],
    },
    "API": {
        "REST Client": ["REST request", "Headers dump", "HTTP methods probe"],
        "GraphQL Client": ["REST request (fallback)"],
        "Webhook Server": ["Run webhook server"],
        "Mock Server": ["Run webhook server (mock)"],
        "Custom": ["REST request"],
    },
    "OSINT": {
        "Username Lookup": ["Cross-site search", "GitHub user", "GitHub repos"],
        "Email Recon": ["MX + DMARC"],
        "Domain Recon": ["DNS + robots + security.txt", "Wayback",
                         "Certificate Transparency", "SPF / DMARC", "Reverse DNS"],
        "Social Scan": ["Cross-site search"],
        "Geolocation": ["IP geolocation"],
        "Custom": ["Domain recon"],
    },
    "Bluetooth": {
        "Device Scan": ["hcitool/bluetoothctl scan"],
        "BLE Tool": ["Bluetooth scan"],
        "GATT Explorer": ["Bluetooth scan"],
        "Custom": ["Bluetooth scan"],
    },
    "WiFi": {
        "Network Scan": ["nmcli/iwlist scan", "MAC vendor lookup"],
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
        "Serial Monitor": ["List serial ports", "Hexdump a file"],
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
        "Device Discovery": ["mDNS browse", "MAC vendor lookup"],
        "MQTT Client": ["mDNS browse"],
        "Telemetry Viewer": ["System info"],
        "Custom": ["mDNS browse"],
    },
    "CLI Utility": {
        "Calculator": ["Evaluate expression", "Unit converter", "Color converter",
                       "Color palette", "Base converter"],
        "Unit Converter": ["Convert units"],
        "Password Gen": ["Generate password", "Generate secure token", "UUID generator"],
        "Color Tool": ["Convert colors", "Generate palette"],
        "Encoder": ["Encoder/Decoder", "Morse code", "ROT all shifts", "Vigenere cipher",
                    "JSON pretty / minify", "TOML viewer", "Diff two strings",
                    "Word count", "Timestamp conversion"],
        "Custom": ["Calculator", "Color tool", "UUID generator"],
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
        "Disk Image": ["Hash a file", "Hexdump"],
        "Memory Dump": ["Hash a file", "Hexdump"],
        "Timeline Builder": ["Log analyzer"],
        "Zip Inspection": ["Inspect zip"],
        "Custom": ["Hash file"],
    },
    "Password Tools": {
        "Generator": ["Generate password", "Generate secure token"],
        "Strength Meter": ["Measure entropy"],
        "Hash Cracker Helper": ["Dictionary cracker"],
        "Vault": ["Snippet manager"],
        "Custom": ["Password generator"],
    },
    "Monitoring": {
        "System Watcher": ["Network sampler", "ARP scan"],
        "Log Tail": ["Log analyzer"],
        "Uptime Pinger": ["Ping sweep", "Traceroute"],
        "Custom": ["Network monitor"],
    },
    "Discord": {
        "Bot Template": ["REST request (Discord API)", "Webhook server"],
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
        "Wallet Tool": ["Hash helper", "Generate token"],
        "Transaction Decoder": ["Hex decode", "Base58"],
        "Custom": ["Price tracker"],
    },
    "Productivity": {
        "Todo": ["Todo list"],
        "Notes": ["Snippet manager"],
        "Timer": ["Countdown", "Cron builder"],
        "Kanban": ["Todo list"],
        "Text Tools": ["Word count", "Diff two strings", "JSON pretty / minify"],
        "Custom": ["Todo list"],
    },
    "Custom": {
        "Custom": ["System info", "Help", "Generate password", "UUID generator",
                   "Timestamp conversion", "JSON pretty / minify"],
    },
}


def commands_for(category: str, subcategory: str) -> List[Command]:
    bucket = COMMANDS.get(category, {})
    if isinstance(bucket, dict):
        names = bucket.get(subcategory, bucket.get("Custom", []))
    else:
        names = bucket
    return [(name, None) for name in names]


__all__ = ["COMMANDS", "commands_for"]