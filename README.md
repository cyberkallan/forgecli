<div align="center">

```
╔══════════════════════════════════════════════════════════════════╗
║   ____                       _____ _      ____ _      ___       ║
║  |  _ \ _ __ __ _  __ _  ___ / ____| |    / ___| |    |_ _|      ║
║  | | | | '__/ _` |/ _` |/ _ \ |  _| |   | |   | |     | |       ║
║  | |_| | | | (_| | (_| |  __/ |_| | |___| |___| |___  | |       ║
║  |____/|_|  \__,_|\__, |\___|\____|_____|\____|_____|___|       ║
║                   |___/                                          ║
║   ForgeCLI — Premium Terminal Tool Builder                      ║
╚══════════════════════════════════════════════════════════════════╝
```

# ForgeCLI

> **Generate complete, production-quality CLI applications from a single guided wizard — themed banners, animated menus, real working commands.**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](#-requirements)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows%20%7C%20Termux-9cf?logo=linux)](#-installation)
[![License](https://img.shields.io/badge/License-MIT-blue)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production-success)](#)
[![Themes](https://img.shields.io/badge/Themes-14%20built--in-ff69b4)](#-theme-engine)
[![Categories](https://img.shields.io/badge/Categories-26%20%7C%20Sub-100%2B-orange)](#)
[![Made With](https://img.shields.io/badge/Made%20with-Rich%20%2B%20Pyfiglet%20%2B%20Questionary-9b59b6)](#)

</div>

---

## 📸 Preview

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   ▄▄▄▄▄ ▄ ▄▄▄ ▄▄▄▄▄    Author: Arjun TM  |  v1.0.0  ⬢       │
│                                                             │
│   █▀█ █ █ █▀█ █ █▀█    ▄▄▄▄▄▄  ▄▄▄▄▄▄  ▄▄▄▄▄▄  ▄▄▄▄▄▄        │
│   █▀▀ █▄█ █▀█ █ █▀█    ▀▄▄▄   ▀▄▄▄    ▀▄▄▄    ▀▄▄▄         │
│   ▀   ▀ ▀ ▀ ▀ ▀ ▀ ▀     ▀▀▀▀   ▀▀▀▀    ▀▀▀▀    ▀▀▀▀         │
│                                                             │
│   ╭────────────────────────╮    ╭──────────────────────────╮  │
│   │  📡 System Information │    │  ⚙  ForgeCLI Dashboard  │  │
│   │  OS: Linux · Python  │    │  1) Create New Tool       │  │
│   │  CWD: ~/projects      │    │  2) Open Existing Tool    │  │
│   │  Net: 12.4 MB/s       │    │  3) Themes                │  │
│   │  Git: ✓ clean         │    │  4) Plugin Manager        │  │
│   ╰────────────────────────╯    ╰──────────────────────────╯  │
└─────────────────────────────────────────────────────────────┘
```

> *Run `forgecli` after install to see the cyberpunk dashboard in action.*

---

## ⚡ What you get

<table>
<tr><th>Feature</th><th>Description</th></tr>
<tr><td>🎨 <b>14 built-in themes</b></td><td>Cyberpunk, Neon, Retro, Mono, Forest, Ocean, and more — plus unlimited custom themes with live preview</td></tr>
<tr><td>🌀 <b>12 animated styles</b></td><td>Matrix Rain, Cyber Loading, Neon Pulse, Retro BIOS, Circuit, Binary, Hex, Glitch, Wave, Pulse, Scan, Fade</td></tr>
<tr><td>🏗 <b>26 categories · 100+ subcategories</b></td><td>Cybersecurity, Networking, OSINT, WiFi, IoT, ESP32, ML, Forensics, Crypto, Discord, Telegram, Developer, Hardware…</td></tr>
<tr><td>🧙 <b>Guided wizard</b></td><td>Quick branding (essentials) or Full branding (30+ fields) — every step previewed before commit</td></tr>
<tr><td>📦 <b>8 export formats</b></td><td>Zip, Tar.gz, Standalone, GitHub-Ready, Termux-Ready, Linux-Ready, Docker, Git</td></tr>
<tr><td>🧩 <b>Plugin system</b></td><td>Drop-in <code>plugins/*.py</code> for generated tools — Updater, Analytics, Logging, Theme Engine, Config, Auto Save, Backup, Notifications</td></tr>
<tr><td>🖥 <b>File manager</b></td><td>Rename, delete, duplicate, move, preview, search, sort — inside the TUI</td></tr>
<tr><td>⚙ <b>Live settings editor</b></td><td>Tweak theme, animation, menu order, autosave, debug mode without editing files</td></tr>
<tr><td>🧠 <b>Smart dep install</b></td><td>Detects Termux, Ubuntu, Debian, Kali, Arch, Fedora, macOS and runs the right <code>apt</code>/<code>pkg</code>/<code>pacman</code>/<code>dnf</code>/<code>brew</code> command</td></tr>
<tr><td>🔍 <b>Live preview</b></td><td>Hot-reload dashboard with animation, banner, and menu before you generate</td></tr>
</table>

---

## 📦 Requirements

| Component | Version | Notes |
|---|---|---|
| **Python** | 3.9 or newer | Pre-installed on macOS · installable via `apt`, `brew`, or Termux `pkg` |
| **pip** | bundled | Comes with Python |
| **git** | any recent | Only for cloning the repo |
| **Terminal** | UTF-8 capable | Windows Terminal, iTerm2, GNOME Terminal, Termux, etc. |

Runtime libs are **installed automatically on first launch**, but you can install them up-front:

```bash
pip install -r requirements.txt
```

> 💡 The generated tools also auto-install their own deps (`rich`, `pyfiglet`, `questionary`) the first time you run them — no manual `pip install` needed for users of your tool.

---

## 🚀 Installation

### 🐧 Linux / 🍎 macOS

```bash
# 1. Clone
git clone https://github.com/cyberkallan/forgecli.git
cd forgecli

# 2. (Recommended) virtualenv
python3 -m venv .venv
source .venv/bin/activate

# 3. Install
pip install -r requirements.txt
pip install -e .

# 4. Run
forgecli        # or: forge | python -m forgecli
```

### 🪟 Windows (PowerShell)

```powershell
git clone https://github.com/cyberkallan/forgecli.git
cd forgecli
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
forgecli
```

### 📱 Termux

Termux ships its own Python — no system Python needed.

```bash
# 1. Update Termux and grab Python + git
pkg update -y && pkg upgrade -y
pkg install -y python git clang libffi openssl

# 2. Clone
git clone https://github.com/cyberkallan/forgecli.git
cd forgecli

# 3. Make the launcher executable (chmod +x on every script)
chmod +x install-termux.sh forgecli.py forge
ls -la forgecli.py forge install-termux.sh
#  -rwxr-xr-x  forgecli.py
#  -rwxr-xr-x  forge
#  -rwxr-xr-x  install-termux.sh

# 4. Install Python deps
pip install --upgrade pip
pip install -r requirements.txt

# 5. Run
./forgecli.py
# or
./forge
```

> 🔧 If `forge` complains about missing modules on first launch, just re-run it — the installer inside the wizard fetches everything.

#### Optional: install to `$PREFIX/bin`

```bash
chmod +x forge forgecli.py
cp forge $PREFIX/bin/forgecli
# now you can run `forgecli` from anywhere in Termux
```

#### Make any generated tool executable

Every tool you generate with ForgeCLI is a real Python project. To run it directly without the `python` prefix:

```bash
cd my-generated-tool
chmod +x main.py run.sh        # chmod +x on every launcher/script
./main.py                       # direct execution
```

---

## 🧭 Quick start

1. **Launch** → run `forgecli` (or `./forgecli.py` on Termux).
2. **Pick** → `Create New Tool` on the dashboard.
3. **Brand** → Quick branding (essentials) or Full branding (30+ fields).
4. **Preview** → confirm the banner, animation, and theme.
5. **Generate** → a complete, runnable project appears in seconds.
6. **Run** → `cd <your-tool> && python main.py` — it just works.

On first launch, ForgeCLI will:

1. ✅ Detect your OS
2. 📥 Auto-install missing system deps (`apt`, `pkg`, `pacman`, `dnf`, `brew`)
3. 🌀 Run the animated startup sequence
4. 📊 Render the cyberpunk dashboard with live system info

---

## 🛠 Built-in commands per category

Every generated project ships with **real, functional** commands for its category — not stubs.

| Category | Examples |
|---|---|
| 🛡 **Cybersecurity** | TCP port scanner · DNS lookup · WHOIS · hash tool · encryption · base64 / hex / URL encoder · packet analyzer · web header scanner · domain recon · log analyzer |
| 🌐 **Networking** | Ping sweep · traceroute · bandwidth test · TCP forwarder |
| 💻 **Developer** | Regex tester · snippet manager · todo · timer · calculator · unit converter · color tool |
| 🕵 **OSINT** | Cross-site username search · email & domain recon |
| 💰 **Crypto** | Live CoinGecko price tracker · transaction decoder |
| 🔧 **Hardware** | Serial port listing · mDNS browse |
| 🔌 **API** | REST client · webhook server |
| 📡 **IoT / ESP32** | Firmware flasher stubs · MQTT publisher |

---

## 🧩 Architecture

```
forgecli/
├── forgecli/
│   ├── core/                platform detection, deps, system info, config, logging
│   │   ├── platform.py
│   │   ├── dependencies.py
│   │   ├── system_info.py
│   │   ├── config.py
│   │   └── logging_utils.py
│   ├── ui/                  animations, banners, theme engine, menu, prompts
│   │   ├── animations.py
│   │   ├── banners.py
│   │   ├── theme.py
│   │   ├── menu.py
│   │   └── prompts.py
│   ├── themes/              14 built-in palettes
│   │   └── builtin.py
│   ├── generators/          project generator + tpl renderer
│   │   ├── project.py
│   │   ├── commands_runtime.py
│   │   └── templates/       all *.tpl files
│   │       ├── main.py.tpl
│   │       ├── theme.py.tpl
│   │       ├── banner.py.tpl
│   │       ├── ui.py.tpl
│   │       ├── commands.py.tpl
│   │       ├── installer.py.tpl
│   │       ├── updater.py.tpl
│   │       ├── utils.py.tpl
│   │       ├── README.md.tpl
│   │       ├── SECURITY.md.tpl
│   │       ├── CONTRIBUTING.md.tpl
│   │       ├── CODE_OF_CONDUCT.md.tpl
│   │       ├── plugins/_example.py.tpl
│   │       └── …
│   ├── wizard/              branding wizard (quick + full)
│   │   └── branding.py
│   ├── dashboard.py         main navigation
│   ├── cli.py               entry point
│   ├── exporter.py          8 export formats
│   ├── profiles.py          user profiles
│   ├── self_update.py       self-update flow
│   ├── validate.py          generated-project validator
│   └── …
├── install-termux.sh        Termux helper
├── forge                    bash launcher
├── forgecli.py              module entry
├── pyproject.toml
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 🎨 Theme engine

Themes are pure Python dicts with these fields:

```python
{
    "primary":   "#00ffe7",
    "secondary": "#ff007a",
    "success":   "#00ff9c",
    "warning":   "#ffcc00",
    "danger":    "#ff4d6d",
    "info":      "#9b8cff",
    "muted":     "#7a7a8c",
    "border":    "#2a2a3a",
    "gradient":  ["#00ffe7", "#ff007a"],
    "style":     "cyberpunk",
}
```

Create unlimited custom themes from **Themes → Create custom theme** in the menu.

---

## 📦 Export formats

| Format | What you get |
|---|---|
| 📦 **Zip** | Single `.zip` archive of the project |
| 📦 **Tar.gz** | Compressed tarball for Unix |
| 📁 **Standalone Folder** | Clean copy, no `__pycache__` |
| 🐙 **GitHub Ready** | Folder + `git init` + initial commit |
| 📱 **Termux Ready** | Includes `install-termux.sh` launcher |
| 🐧 **Linux Ready** | `.desktop` entry + bash launcher |
| 🐳 **Docker Project** | Adds `Dockerfile` + `docker-compose.yml` |
| 🔀 **Git Repository** | Full git history preserved |

---

## 🧩 Plugin system (generated tools)

Every tool you generate ships with a `plugins/` folder. Drop a `.py` file in there and expose a `register(ctx)` function:

```python
# my-tool/plugins/hello.py
def register(ctx):
    def hello():
        ctx.console.print("[bold cyan]Hello from a plugin![/]")
    return [("Say hello", hello)]
```

It will appear in the menu automatically. A broken plugin is reported to the console but never crashes the tool.

---

## 🔧 Troubleshooting

<details>
<summary><b>UnicodeEncodeError on Windows</b></summary>

Generated tools call `_force_utf8_io()` at startup to set UTF-8 on `stdout`/`stderr`. If you still see encoding errors, run inside **Windows Terminal** (not legacy `cmd.exe`) or set:

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001
```
</details>

<details>
<summary><b>Termux: pip fails with OpenSSL</b></summary>

```bash
pkg install -y clang libffi openssl
pip install --upgrade pip
pip install -r requirements.txt
```
</details>

<details>
<summary><b>macOS: externally-managed-environment error</b></summary>

Use a venv:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
</details>

<details>
<summary><b>chmod +x doesn't seem to stick</b></summary>

Make sure you're not on a filesystem mounted with `noexec` (e.g. some Android external storage). On Termux, run from the home directory (`~`) and avoid `/sdcard`.

```bash
mount | grep noexec
chmod +x main.py && file main.py   # file should say "executable"
```
</details>

---

## 👤 Author

<div align="center">

**Arjun TM**

[![GitHub](https://img.shields.io/badge/GitHub-cyberkallan-181717?logo=github)](https://github.com/cyberkallan)
[![Instagram](https://img.shields.io/badge/Instagram-imarjunarz-E4405F?logo=instagram&logoColor=white)](https://instagram.com/imarjunarz)

</div>

---

## 📜 License

[MIT](LICENSE) — © Arjun TM. Forge freely.

---

## 💬 Contributing

Issues, feature requests, and PRs welcome. ForgeCLI is built to be extensible — new categories, themes, animations, and export formats slot cleanly into the existing architecture. See [CONTRIBUTING.md](CONTRIBUTING.md).

<div align="center">

<sub>Made with 🛠 by humans who love the terminal.</sub>

</div>