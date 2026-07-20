<div align="center">

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║                 {{LOGO_TEXT}}                                    ║
║                                                                  ║
║              {{TAGLINE}}                                         ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

# {{LOGO_TEXT}}

> {{TAGLINE}}

![status](https://img.shields.io/badge/status-{{STATUS}}-{{BADGE_COLOR}})
![license](https://img.shields.io/badge/license-{{LICENSE_BADGE}}-blue)
![python](https://img.shields.io/badge/python-{{PYTHON_BADGE}}-blue)
![platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows%20%7C%20Termux-9cf)

{{DESCRIPTION}}

---

## 📸 Preview

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                       {{LOGO_TEXT}}                         │
│                                                             │
│   ╭────────────────────────╮    ╭──────────────────────────╮  │
│   │  📡 System Information │    │  ⚙  Commands            │  │
│   │  OS: … · Python …     │    │  1) …                    │  │
│   │  CWD: …               │    │  2) …                    │  │
│   │  Net: …               │    │  3) …                    │  │
│   ╰────────────────────────╯    ╰──────────────────────────╯  │
└─────────────────────────────────────────────────────────────┘
```

> Run the tool to see the **{{THEME_NAME}}** theme, the **{{STARTUP_ANIMATION}}** animation, and the live system info panel.

---

## ✨ Features

- 🎨 **{{THEME_NAME}}** themed banner and menus
- 🌀 **{{STARTUP_ANIMATION}}** startup animation
- 📦 Auto-installing runtime dependencies on first launch
- 📊 Live system information (Python, terminal, network, git)
- 🔄 Update checker against PyPI
- 🧩 Pluggable commands for **{{SUBCATEGORY}}** under the **{{CATEGORY}}** category
- 📱 Drop-in plugin support via `./plugins/*.py`
- 🪟 UTF-8 forced on Windows consoles — rich renders every glyph cleanly

---

## 🧰 Available commands

{{COMMANDS_MD}}

The generated tool ships with real, functional commands. Pick one at the animated menu and follow the prompts.

---

## 📦 Requirements

| Component | Version | Notes |
|---|---|---|
| **Python** | {{PYTHON_VERSION}} | Auto-detected on first run |
| **Terminal** | UTF-8 capable | Windows Terminal, iTerm2, GNOME Terminal, Termux |

Runtime libs (`rich`, `pyfiglet`, `questionary`) are **installed automatically** the first time you run `main.py`.

---

## 🚀 Installation

### 🐧 Linux / 🍎 macOS

```bash
git clone {{GITHUB_REPO}}
cd {{SLUG}}

# (Recommended) virtualenv
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
chmod +x main.py run.sh            # chmod +x on every launcher
./main.py                          # or: python main.py
```

Install as a system tool:

```bash
pip install .
{{COMMAND_NAME}}
```

### 🪟 Windows (PowerShell)

```powershell
git clone {{GITHUB_REPO}}
cd {{SLUG}}
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

> 🔤 The tool calls `_force_utf8_io()` on startup so box-drawing, emoji, and any Unicode render reliably on legacy `cmd.exe` too.

### 📱 Termux

```bash
# 1. Setup
pkg update -y && pkg upgrade -y
pkg install -y python git clang libffi openssl

# 2. Clone
git clone {{GITHUB_REPO}} && cd {{SLUG}}

# 3. Make every launcher executable
chmod +x main.py run.sh install-termux.sh
ls -la main.py run.sh install-termux.sh
#  -rwxr-xr-x  main.py
#  -rwxr-xr-x  run.sh
#  -rwxr-xr-x  install-termux.sh

# 4. Install deps
pip install --upgrade pip
pip install -r requirements.txt

# 5. Run
./main.py
```

Optional: install into `$PREFIX/bin`:

```bash
cp main.py $PREFIX/bin/{{COMMAND_NAME}}
chmod +x $PREFIX/bin/{{COMMAND_NAME}}
{{COMMAND_NAME}}
```

---

## ⚙️ Usage

```bash
python main.py
# or, after installing
{{COMMAND_NAME}}
# or on Termux, after chmod +x
./main.py
```

---

## 🎛 Configuration

Edit `config.json` or `theme.json` to change the look and behaviour. The generated `theme.json` matches the selected theme; tweak colours and reload to apply.

---

## 🧩 Plugin system

Drop `.py` files into `./plugins/`. Each may expose `register(ctx) -> [(label, callable), ...]`:

```python
# plugins/hello.py
def register(ctx):
    def hello():
        ctx.console.print("[bold cyan]Hello![/]")
    return [("Say hello", hello)]
```

It will appear in the menu automatically. Broken plugins are reported but never crash the tool.

---

## 🧪 Examples

```python
from commands import commands_for
print([name for name, _ in commands_for("{{CATEGORY}}", "{{SUBCATEGORY}}")])
```

---

## 🛠 Troubleshooting

<details>
<summary><b>UnicodeEncodeError on Windows</b></summary>

The tool already calls `_force_utf8_io()` to set UTF-8 on `stdout`/`stderr`. If you still see encoding errors, run inside **Windows Terminal** (not legacy `cmd.exe`) or set:

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
<summary><b>chmod +x doesn't stick</b></summary>

You're probably on a `noexec` filesystem (e.g. `/sdcard`). Move the project to Termux home (`~`) and retry:

```bash
mount | grep noexec
chmod +x main.py && file main.py
```
</details>

---

## 👤 Author

**{{AUTHOR}}**
- GitHub: {{GITHUB}}
- Instagram: {{INSTAGRAM}}
- Website: {{WEBSITE}}
- Email: {{EMAIL}}

---

## 📜 License

{{LICENSE}} — Copyright (c) {{YEAR}} {{AUTHOR}}.

---

## 🤝 Contributing

Issues and pull requests welcome at {{GITHUB}}. See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 🗺 Roadmap

- 🌐 Web dashboard
- 🎨 Theme marketplace
- 🧩 Plugin store
- ☁️ Cloud sync
- 🤖 AI assistant

---

## 💬 Support

- Documentation: {{DOCS_URL}}
- Support: {{SUPPORT_URL}}
- Donate: {{DONATION_URL}}

<div align="center">

<sub>Built with 🛠 by [ForgeCLI]({{GITHUB}}).</sub>

</div>