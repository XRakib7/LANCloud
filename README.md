# 📂 Online File Manager

> **Turn any computer into your personal cloud — in 30 seconds.** Share, access, and manage your files from your phone, tablet, laptop, or any other device on the same WiFi. No accounts, no sign-ups, no cables, no cloud storage limits, no monthly fees. Your files never leave your home network.

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#contributing)

---

## 🌟 What Is This?

**Online File Manager** gives your computer a clean, beautiful web interface for your files — and then shares it with every device on your WiFi network.

Run it on your PC (or a VM, or a spare laptop, or a Raspberry Pi), and instantly open your files from:

- 📱 **Your phone** — grab photos, documents, or music from your PC while on the couch
- 💻 **Another laptop** — pull that report off your desktop without emailing yourself
- 📟 **A tablet** — read PDFs straight off your computer's drive
- 🖥️ **A virtual machine** — finally an easy way to move files in and out of VirtualBox VMs

All you need is a web browser. That's it. **Nothing else needed.**

---

## 💡 Why You Need This

Ever run into these situations?

| 😩 The Problem | ✅ With Online File Manager |
|---|---|
| "How do I get this file from my PC to my phone?" | Open the network URL on your phone, tap download. Done. |
| Emailing files to yourself like a caveman | Your files are one browser tab away, always |
| USB cables, pendrives, Bluetooth pairing rituals | Zero hardware, zero pairing — just WiFi and a browser |
| Cloud uploads of large files taking forever | Transfers happen directly over your local network — gigabit speed |
| Privacy worries about files on Google Drive / Dropbox | Your files **never leave your machine**. Nothing is uploaded anywhere |
| Free cloud storage is full, paywall asking for a subscription | Unlimited storage — your disk is the limit |
| Setting up Samba, NFS, or SSH feels like rocket science | One command: `python app.py`. You're done |

**In short:** it's your own private cloud, without the cloud.

---

## 🚀 What It Can Do

Everything you'd expect from a full file manager — right in your browser:

| | Feature | What You Get |
|---|---|---|
| 📂 | **Browse everything** | Navigate your entire filesystem with breadcrumbs, from your home directory down to any folder |
| ⬆️ | **Upload files** | Send files *to* your computer from any device — multiple files at once |
| 📁 | **Upload whole folders** | Drop an entire folder (with subfolders) from your phone straight onto your PC |
| ⬇️ | **Download files** | Grab any single file to any device instantly |
| 📦 | **Download folders as ZIP** | One click, the whole folder gets zipped and sent to you |
| ✏️ | **Edit text files in-browser** | Fix a config, tweak a script, update notes — edit and save without downloading anything |
| 🆕 | **Create folders** | New folders created right from the toolbar |
| 🔀 | **Rename** | Rename any file or folder from the browser |
| 🗑️ | **Delete** | Remove files and folders (with confirmation — no accidental wipes) |
| 🔍 | **Instant search** | Live filtering as you type — find that one file in a folder of hundreds |
| ↕️ | **Sortable columns** | Sort by Name, Size, Type, or Date Modified with a click |
| 🌓 | **Dark mode** | Easy on the eyes at night — your preference is remembered |
| 📱 | **Fully responsive** | Looks and works great on phones, tablets, and desktops |
| 🧠 | **Smart file icons** | Instantly recognizes code, text, images, video, audio, archives, and PDFs |

### 💪 How Powerful Is It?

- **Full filesystem access** — not a sandboxed "storage folder" like cloud apps. Browse your *entire* disk, including the root directory (`/`) if you want.
- **Gigabit transfers** — everything moves over your local WiFi/LAN, not through some server across the world. A 2 GB file takes seconds, not an hour.
- **Unlimited space** — the only limit is your hard drive.
- **Unlimited devices** — phone, laptop, tablet, smart TV browser, anything with a browser on the network.
- **True two-way street** — unlike most "sharing" tools that only send, this one uploads *and* downloads *and* edits *and* organizes. It's a complete file manager, not just a file dropper.
- **Runs anywhere Python runs** — Windows, macOS, Linux, a VM, a Raspberry Pi, an old laptop gathering dust in a drawer. Turn that old machine into a home file server in one command.

---

## 🏁 Getting Started

### Prerequisites

Only one thing:

- **Python 3** installed ([python.org](https://www.python.org/downloads/))

That's it. No database, no Node.js, no Docker, no config files.

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/rakibhossain/online-file-manager.git
cd online-file-manager

# 2. Install the single dependency
pip install -r requirements.txt
```

### Run It

```bash
python app.py
```

You'll see something like:

```
Online File Manager running at:
  Local:   http://127.0.0.1:5000
  Network: http://192.168.1.10:5000
  Home:    /home/yourname
  Root:    /
```

- **On the same computer:** open `http://127.0.0.1:5000`
- **On your phone / any other device on the WiFi:** open the **Network** address, e.g. `http://192.168.1.10:5000`

🎉 **That's the whole setup.** Your computer is now a personal cloud.

> 💡 **Tip:** Bookmark the network address on your phone. As long as this app is running on your PC, your files are one tap away.

---

## 📖 How To Use

| Action | How |
|---|---|
| **Browse** | Click a folder to open it, click `..` to go up, or use the breadcrumb trail at the top |
| **Upload a file** | Click **Upload File** — pick one or many — they land in the current folder |
| **Upload a folder** | Click **Upload Folder** — the whole folder structure uploads intact |
| **Download a file** | Tap the ↓ icon next to it |
| **Download a folder** | Click **Download Folder** — you get a ZIP |
| **Edit a text file** | Tap the ✏️ icon, make your change, hit **Save Changes** |
| **Rename** | Tap the rename icon and type a new name |
| **Delete** | Tap 🗑️ and confirm (permanent — be careful!) |
| **Create a folder** | Click **New Folder** and name it |
| **Search** | Just start typing in the search box — the list filters live |
| **Sort** | Click any column header (Name / Size / Type / Modified) |
| **Dark mode** | Toggle the theme switch — it's remembered across visits |

### Root access

Start from your home directory, but a **Root** option lets you browse the entire filesystem — perfect for editing system configs on a VM.

---

## 🖥️ Running on a Virtual Machine (VirtualBox)

This is a killer use case: getting files in and out of a VM without Samba, SSH, or shared-folder headaches.

### Option A — Bridged Adapter (recommended)

1. VM Settings → Network → Attach to: **Bridged Adapter**
2. Start the VM — it gets its own IP on your WiFi
3. From your host or phone, open `http://<VM-IP>:5000`

### Option B — NAT with Port Forwarding

1. VM Settings → Network → Attach to: **NAT Network** → Port Forwarding:

   | Protocol | Host IP | Host Port | Guest Port |
   |----------|---------|-----------|------------|
   | TCP | 127.0.0.1 | 5000 | 5000 |

2. Allow the port in the VM's firewall:

   ```bash
   sudo ufw allow 5000/tcp
   ```

3. Open `http://127.0.0.1:5000` from your host machine.

---

## 🔒 A Word On Security

This is designed as a **personal, home-network tool** — it has **no login** by design, so anyone on your WiFi could access the files.

That's perfectly fine for:

- ✅ Your home WiFi (family network)
- ✅ A trusted VM setup
- ✅ Quick personal file transfers

Do **not** run it on:

- ❌ Public WiFi (cafés, airports)
- ❌ Networks with strangers on them
- ❌ Port-forwarded to the internet

**Hardening tips if you need them:** change `app.secret_key` in `app.py`, bind to `127.0.0.1` for local-only access, and put it behind an authenticating reverse proxy (e.g., Nginx) if you ever expose it beyond your network.

---

## 🛠️ Customization

- **Port:** change `port=5000` in the last line of `app.py`
- **Theme & styling:** edit the CSS variables in the templates
- **File-type icons:** extend the extension maps in the templates

---

## 🗺️ Roadmap

- [ ] Login/password protection
- [ ] Image, video, and PDF preview in the browser
- [ ] Copy / move files between directories
- [ ] Multi-select and bulk actions
- [ ] Drag-and-drop uploads
- [ ] Dockerfile for one-command deployment

---

## 🤝 Contributing

Suggestions and pull requests are welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit: `git commit -m "Add your feature"`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

Found a bug? Open an issue first so we can discuss it.

---

## 📄 License

MIT License — free to use, modify, and share. See the [LICENSE](LICENSE) file.

---

## 👤 Author

**Rakib** — Personal project
🔗 GitHub: https://github.com/rakibhossain

---

_Made with ❤️ and Flask. Your files, your network, your cloud._
