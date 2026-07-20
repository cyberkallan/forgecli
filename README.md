# ForgeCLI

> **Premium Terminal Tool Builder — generate complete, production-quality CLI applications from a single guided wizard.**

ForgeCLI is a real, fully working Python application that builds real, runnable CLI tools for you. No templates-with-placeholders, no fake code, no TODOs. Every generated project ships with a themed banner, animated menu, system info dashboard, update checker, auto-installer, and a curated set of **functional** commands for the chosen category.

---

## ✨ What you get

- 🎨 **14 built-in themes** + unlimited custom themes with live preview
- 🌀 **12 animated startup/loading styles** (Matrix Rain, Cyber Loading, Neon Pulse, Retro BIOS, Circuit, Binary, Hex, …)
- 🏗 **26 tool categories** (Cybersecurity, Networking, OSINT, WiFi, IoT, ESP32, ML, Forensics, Crypto, Discord, Telegram, …) with **100+ subcategories**
- 🧙 **Branding wizard** that asks the right questions and previews everything before generation
- 📦 **8 export formats** (Zip, Tar.gz, Standalone, GitHub Ready, Termux, Linux, Docker, Git)
- 🧩 **Plugin system** (Updater, Analytics, Logging, Theme Engine, Config, Auto Save, Backup, Notifications, …)
- 🖥 **File manager** (rename, delete, duplicate, move, preview, search, sort)
- ⚙ **Live settings editor**
- 🧠 **Auto dependency detection & installation** for Termux, Ubuntu, Debian, Kali, Arch, Fedora, and macOS
- 🔍 **Live preview mode** with hot reload

## 🚀 Installation

```bash
git clone https://github.com/cyberkallan/forgecli
cd forgecli
pip install -r requirements.txt
pip install -e .
```

Now run it:

```bash
forgecli
# or
forge
# or
python -m forgecli
```

On first launch, ForgeCLI will:

1. Detect your operating system
2. Auto-install missing system dependencies (`apt`, `pkg`, `pacman`, `dnf`, or `brew`)
3. Run an animated startup sequence
4. Display the cyberpunk dashboard with a system info panel

## 🧭 Quick start

1. Pick **Create New Tool** on the dashboard
2. Choose **Quick branding** (essentials) or **Full branding** (30+ fields)
3. Confirm the summary
4. ForgeCLI generates a complete, runnable tool in seconds
5. Run `python main.py` inside the generated folder — it works immediately

## 🛠 Built-in commands per category (excerpt)

Every generated project ships with **real, functional** commands for its category:

| Category | Examples |
|---|---|
| Cybersecurity | TCP port scanner, DNS lookup, WHOIS, hash tool, encryption, base64/hex/URL encoder, packet analyzer, web header scanner, domain recon, log analyzer |
| Networking | Ping sweep, traceroute, bandwidth test, TCP forwarder |
| Developer | Regex tester, snippet manager, todo, timer, calculator, unit converter, color tool |
| OSINT | Cross-site username search, email & domain recon |
| Crypto | Live CoinGecko price tracker, transaction decoder |
| Hardware | Serial port listing, mDNS browse |
| API | REST client, webhook server |

## 🧩 Architecture

```
forgecli/
├── forgecli/
│   ├── core/          platform detection, deps, system info, config, logging
│   ├── ui/            animations, banners, theme engine, menu, prompts
│   ├── themes/        14 built-in palettes
│   ├── generators/    templates + the project generator
│   ├── wizard/        branding wizard (full + quick)
│   ├── dashboard.py   main navigation
│   ├── cli.py         entry point
│   └── ...
├── pyproject.toml
├── requirements.txt
└── LICENSE
```

## 🎨 Theme engine

Themes are pure JSON-style objects with `primary`, `secondary`, `success`, `warning`, `danger`, `info`, `muted`, `border`, `gradient`, `style` fields. Create unlimited custom themes from the **Themes → Create custom theme** menu.

## 📦 Export formats

| Format | What you get |
|---|---|
| Zip / Tar.gz | A single archive of the project |
| Standalone Folder | A clean copy with no `__pycache__` |
| GitHub Ready | Folder + `git init` + initial commit |
| Git Repository | Bare-friendly copy with version control |
| Termux Ready | Includes `install-termux.sh` launcher |
| Linux Ready | Includes `.desktop` entry and bash launcher |
| Docker Project | Adds `Dockerfile` + `docker-compose.yml` |
| Git Repository | Full git history |

## 🔧 Requirements

- Python **3.9+**
- `rich`, `pyfiglet`, `questionary`, `colorama` (installed automatically if missing)

## 👤 Author

**Arjun TM**
- GitHub: https://github.com/cyberkallan
- Instagram: https://instagram.com/imarjunarz

## 📜 License

MIT License — see [LICENSE](LICENSE).

## 💬 Contributing

Issues, feature requests, and PRs are welcome. ForgeCLI is built to be extensible — new categories, themes, animations, and export formats all slot cleanly into the existing architecture.
