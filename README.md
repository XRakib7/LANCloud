# 📂 LANCloud — Online File Manager

> **Turn any computer into your personal cloud — in 30 seconds.** Share, access, and manage your files from your phone, tablet, laptop, or any other device on the same WiFi. No accounts, no sign-ups, no cables, no cloud storage limits, no monthly fees. Your files never leave your home network.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#contributing)

---

## 🌟 What Is This?

**LANCloud** gives your computer a clean, beautiful web interface for your files — and then shares it with every device on your WiFi network.

Run it on your PC (or a VM, or a spare laptop, or a Raspberry Pi), and instantly open your files from:

- 📱 **Your phone** — grab photos, documents, or music from your PC while on the couch
- 💻 **Another laptop** — pull that report off your desktop without emailing yourself
- 📟 **A tablet** — read PDFs straight off your computer's drive
- 🖥️ **A virtual machine** — finally an easy way to move files in and out of VirtualBox VMs

All you need is a web browser. That's it. **Nothing else needed.**

Works the same on **Windows, Linux, macOS**, and virtual machines.

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
| 📂 | **Browse everything** | Navigate your entire filesystem with breadcrumbs. On Windows, use the 🌐 button to switch between drives (`C:`, `D:`, USB drives, …) |
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

- **Full filesystem access** — not a sandboxed "storage folder" like cloud apps. Browse your *entire* disk, including every drive on Windows.
- **Gigabit transfers** — everything moves over your local WiFi/LAN, not through some server across the world. A 2 GB file takes seconds, not an hour.
- **Unlimited space** — the only limit is your hard drive.
- **Unlimited devices** — phone, laptop, tablet, smart TV browser, anything with a browser on the network.
- **True two-way street** — unlike most "sharing" tools that only send, this one uploads *and* downloads *and* edits *and* organizes. It's a complete file manager, not just a file dropper.
- **Runs anywhere Python runs** — Windows, macOS, Linux, a VM, a Raspberry Pi, an old laptop gathering dust in a drawer. Turn that old machine into a home file server in one command.

---

## 🏁 Getting Started

### Prerequisites

Only one thing:

- **Python 3.8 or newer** installed ([python.org](https://www.python.org/downloads/))

That's it. No database, no Node.js, no Docker, no config files.

> On Windows, tick **"Add Python to PATH"** in the installer. The `py` launcher is recommended.

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/XRakib7/LANCloud.git
cd LANCloud

# 2. Install the dependency
python -m pip install -r requirements.txt
```

On Windows, use the Python launcher:

```bat
py -m pip install -r requirements.txt
```

`requirements.txt` uses a flexible version range (`Flask>=2.3,<4`), so pip picks a Flask version compatible with your Python. You no longer need to edit it manually.

### Run It

```bash
python app.py
```

or on Windows:

```bat
py app.py
```

You can also use the included launcher scripts:

- **Windows:** double-click `run_windows.bat` (installs Flask automatically if missing)
- **Linux/macOS:** `./run_linux.sh`

You'll see something like:

```
LANCloud is running:
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

## 🪟 Running on Windows

Windows needs one extra step: **allow the port through Windows Firewall**. Windows blocks incoming connections by default, which is the most common reason the app loads on the PC but not on your phone.

### Option A — the easy way

1. Right-click **`allow_firewall_windows.bat`** → **Run as administrator**.
2. Make sure your WiFi network is set to **Private** (Settings → Network & Internet → WiFi → your network → Network profile type).
3. Open the **Network** URL printed by `app.py` on your phone.

### Option B — manual command

Open **Command Prompt as Administrator** and run:

```bat
netsh advfirewall firewall add rule name="LANCloud" dir=in action=allow protocol=TCP localport=5000 profile=private,domain
```

To remove the rule later:

```bat
netsh advfirewall firewall delete rule name="LANCloud"
```

### Finding your Windows IP address

```bat
ipconfig
```

Look for **IPv4 Address** under your active WiFi/Ethernet adapter (for example `192.168.1.107`). Then open:

```
http://192.168.1.107:5000
```

### Browsing other drives

Click the 🌐 button (next to the home button) to see **This PC** and every available drive. Click a drive to browse it. This works even when the project is on `D:` and your home folder is on `C:` — the app keeps Windows drive letters intact.

### Still can't connect from another device?

- Phone and PC must be on the **same WiFi network** (not mobile data, not a guest network).
- Turn off **VPN** on either device while testing.
- Some routers have **AP isolation / client isolation** enabled — turn it off for your home network.
- Make sure the Flask window is still running and shows `Running on http://0.0.0.0:5000`.
- Try the `127.0.0.1` URL on the PC first. If that works but the LAN URL does not, it is almost always the firewall or network profile.

---

## 📖 How To Use

| Action | How |
|---|---|
| **Browse** | Click a folder to open it, click `..` to go up, or use the breadcrumb trail at the top |
| **Switch drives (Windows)** | Click the 🌐 button to open **This PC** |
| **Upload a file** | Click **Upload File** — pick one or many — they land in the current folder |
| **Upload a folder** | Click **Upload Folder** — the whole folder structure uploads intact |
| **Download a file** | Tap the ↓ icon next to it |
| **Download a folder** | Click the ↓ icon next to a folder — you get a ZIP |
| **Edit a text file** | Tap the ✏️ icon, make your change, hit **Save Changes** |
| **Rename** | Tap the rename icon and type a new name |
| **Delete** | Tap 🗑️ and confirm (permanent — be careful!) |
| **Create a folder** | Click **New Folder** and name it |
| **Search** | Just start typing in the search box — the list filters live |
| **Sort** | Click any column header (Name / Size / Type / Modified) |
| **Dark mode** | Toggle the theme switch — it's remembered across visits |

### Root access

Start from your home directory, but the **🌐 / Root** button lets you browse the entire filesystem — perfect for editing system configs on a VM or reaching another Windows drive.

> Folder sizes are calculated with a small time budget so opening a huge folder like `C:\Windows` does not freeze the page. A folder that is too large to scan quickly shows `—` instead of a size.

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

## 🧰 Troubleshooting

### `pip install -r requirements.txt` cannot find Flask

- Use the command that matches your Python:
  - Windows: `py -m pip install -r requirements.txt`
  - Linux/macOS: `python3 -m pip install -r requirements.txt`
- Upgrade pip first: `python -m pip install --upgrade pip`
- Check your Python version: `python --version` (3.8+ required).
- The requirements file is now `Flask>=2.3,<4`, so it no longer demands one exact version.

### The page loads on the PC but not on my phone

See **[Running on Windows](#-running-on-windows)** above. On Linux, allow the port with `sudo ufw allow 5000/tcp`.

### `Address already in use` / port 5000 is busy

Run on another port:

```bash
# Linux/macOS
PORT=8080 python app.py
```

```bat
:: Windows Command Prompt
set PORT=8080
py app.py
```

```powershell
# Windows PowerShell
$env:PORT="8080"
py app.py
```

Then open `http://<your-ip>:8080`. If you use the firewall script, run it with the same port: `allow_firewall_windows.bat 8080`.

### A page shows "Internal Server Error"

Run the app from a terminal and look at the traceback printed there. Common causes are permission-protected folders and files locked by another program. The app catches most of these and shows a flash message instead of crashing.

### The app feels slow in `C:\Windows` or a huge folder

Folder sizes are sampled with a time limit on purpose. The listing itself is fast; only the size column is approximate (`—` means "too large to scan quickly"). You can still open, download, rename, and delete everything.

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

**Hardening tips if you need them:**

- Set a fixed secret key so sessions survive restarts: `SECRET_KEY=your-long-random-value` (or `set SECRET_KEY=...` on Windows).
- Bind to `127.0.0.1` for local-only access: `HOST=127.0.0.1 python app.py`.
- Put it behind an authenticating reverse proxy (e.g., Nginx) if you ever expose it beyond your network.
- Debug mode is **off by default**. Only enable it on your own machine for development: `FLASK_DEBUG=1 python app.py`. Never expose debug mode to a LAN.

---

## 🛠️ Customization

- **Port:** set the `PORT` environment variable (default `5000`)
- **Bind address:** set `HOST` (default `0.0.0.0`; use `127.0.0.1` for local-only)
- **Secret key:** set `SECRET_KEY`
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

**XRakib7** — Personal project
🔗 GitHub: https://github.com/XRakib7

---

_Made with ❤️ and Flask. Your files, your network, your cloud._
