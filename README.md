# Flask File Manager

> A lightweight, self-hosted web-based file manager built with Flask. Browse, upload, download, edit, rename, and delete files and folders from any device on your network — no cloud account, no third-party dependency, your files stay on your own machine.

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.3-000000?logo=flask)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## Table of Contents

- [About](#about)
- [Why This Project Exists](#why-this-project-exists)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Screenshots](#screenshots)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Application](#running-the-application)
- [How to Use](#how-to-use)
- [VirtualBox / Network Access](#virtualbox--network-access)
- [Security](#security)
- [Customization](#customization)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

---

## About

**Flask File Manager** is a personal, self-hosted file management web application. It runs a small Flask server on your computer (or virtual machine) and exposes a clean, responsive browser interface so you can manage your filesystem from any device on the same network.

It is ideal for accessing files on a headless Debian VM (e.g., VirtualBox) from your Windows/macOS/Linux host or phone without setting up Samba/NFS shares, SSH/SCP, or uploading to a third-party cloud.

---

## Why This Project Exists

Managing files on a remote machine, virtual machine, or headless server usually forces you into one of these painful options:

| Typical Approach | Pain Point |
|------------------|------------|
| Samba / NFS shares | Complex setup, firewall config, not beginner-friendly |
| SSH / SCP | Command-line only, not convenient for quick edits |
| Google Drive / Dropbox | Privacy concerns, third-party dependency, sync delays |
| Heavy file-manager services | Overkill for personal use, hard to maintain |

**Flask File Manager** removes that friction:

- ✅ **Zero accounts** — your files never leave your machine
- ✅ **One-command setup** — `pip install flask && python app.py`
- ✅ **Accessible from any browser** on the same WiFi (phone, laptop, tablet)
- ✅ **Mobile-friendly** responsive UI with light/dark theme
- ✅ **Folder upload/download as ZIP**, inline text editing, live search, sortable columns

Whether you're moving files between a VM and your laptop, editing configs on a remote box, or just want private self-hosted file access — this tool gets out of your way.

---

## Key Features

| Feature | Description |
|---------|-------------|
| 📂 **Browse** | Navigate directories with breadcrumb trails and parent-directory links |
| ⬆️ **Upload Files** | Upload one or many files to the current directory |
| 📁 **Upload Folders** | Upload entire folder structures (browser `webkitdirectory` support) |
| ⬇️ **Download Files** | Download individual files directly from the browser |
| 📦 **Download Folders** | Download any folder as a ZIP archive |
| ✏️ **Edit Text Files** | Open and edit text/source files inline in the browser |
| 🆕 **New Folder** | Create folders from the toolbar |
| 🗑️ **Delete** | Remove files and folders (with confirmation dialog) |
| 🔍 **Search** | Client-side live search to filter files instantly |
| 🔀 **Sort** | Clickable, sortable columns (Name, Size, Type, Date Modified) |
| 🌓 **Dark Mode** | Light/dark theme toggle, persisted in `localStorage` |
| 📱 **Responsive** | Works on desktop and mobile browsers |
| 🔔 **Flash Messages** | Success/error feedback after every action |

---

## Tech Stack

- **Backend:** Python 3 + Flask (micro web framework)
- **Frontend:** Vanilla HTML5, CSS3 (CSS custom properties), vanilla JavaScript — no build step, no frontend frameworks
- **Templating:** Jinja2 (Flask's built-in templating engine)
- **Packaging:** `requirements.txt` with a pinned Flask version

---

## Project Structure

```
filemanager/
├── app.py              # Flask application — all routes and file logic
├── requirements.txt    # Python dependencies (Flask==3.1.3)
├── README.md           # This file
├── LICENSE             # MIT License
├── .gitignore          # Git ignore rules
└── templates/
    ├── index.html      # Main file-browser UI
    ├── edit.html       # Text-file editor page
    └── rename.html     # Rename dialog page
```

---

## Screenshots

> Add screenshots here showing:
> 1. **File Browser** — table view with icons, file sizes, dates, and action buttons
> 2. **Text Editor** — monospace editor for quick config or code tweaks
> 3. **Dark Theme** — easy on the eyes for night sessions

---

## Getting Started

### Prerequisites

- Python 3.x
- `pip` (Python package installer)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/flask-file-manager.git
cd flask-file-manager

# Install dependencies
pip install -r requirements.txt
# (or: pip3 install -r requirements.txt)
```

### Running the Application

```bash
python app.py
# (or: python3 app.py)
```

You will see output like this:

```
File Manager running at:
  Local:   http://127.0.0.1:5000
  Network: http://192.168.1.xx:5000
  Home:    /home/yourname
  Root:    /
```

- Open `http://127.0.0.1:5000` on the same machine.
- Use the **Network** URL from any other device on the same WiFi.

---

## How to Use

1. **Browse** — Click a folder name to go inside; click `..` to go up. Use the breadcrumb trail at the top to jump between levels.
2. **Upload files** — Click **Upload File**, select one or more files; they save to the current folder.
3. **Upload folders** — Click **Upload Folder** and select a folder; its contents upload preserving the folder structure.
4. **Create folder** — Click **New Folder** and type a name.
5. **Download a file** — Click the download icon (↓) next to any file.
6. **Download a folder** — Click **Download Folder** to grab the whole folder as a ZIP.
7. **Edit a text file** — Click the edit icon (✏️) next to a text file, make changes, then **Save Changes**.
8. **Rename** — Click the rename icon next to any item and enter a new name.
9. **Delete** — Click the trash icon (🗑️) and confirm — deletion is permanent.
10. **Search** — Type in the search box to filter files as you type.
11. **Sort** — Click any column header (Name, Size, Type, Date Modified) to sort the list.

---

## VirtualBox / Network Access

This app was designed to run on a Debian VM in VirtualBox and be reachable from your host and other LAN devices.

### Option A — Bridged Adapter (recommended)

VM Settings → Network → Attach to: **Bridged Adapter**.  
The VM gets its own IP on your physical network; use that IP with port `5000` from other devices.

### Option B — NAT Network with port forwarding

VM Settings → Network → Attach to: **NAT Network** → Port Forwarding → add a rule:

| Field | Value |
|-------|-------|
| Name | FileManager |
| Protocol | TCP |
| Host IP | 127.0.0.1 |
| Host Port | 5000 |
| Guest IP | (leave empty) |
| Guest Port | 5000 |

Then allow the port through the VM firewall:

```bash
sudo ufw allow 5000/tcp
```

---

## Security

⚠️ **This app is intended for trusted local networks only.** It has **no authentication** and exposes your filesystem.

Before exposing it beyond `localhost`:

- Change `app.secret_key` in `app.py`
- Add authentication (login middleware)
- Serve over HTTPS (e.g., Nginx reverse proxy + Certbot)
- Restrict allowed upload file types and sizes
- Bind to `127.0.0.1` instead of `0.0.0.0` if you only need local access

---

## Customization

- **Port:** Change `app.run(host='0.0.0.0', port=5000, debug=True)` in `app.py`
- **Base directory:** Modify `BASE_DIR` / `HOME_DIR` at the top of `app.py`
- **Styling:** Edit the CSS variables in the HTML templates (`:root` and `[data-theme="dark"]`)
- **File-type icons:** Extend the extension maps in `index.html`

---

## Roadmap

- [ ] User authentication (login/password)
- [ ] HTTPS deployment guide
- [ ] Image/PDF preview in the browser
- [ ] Copy/move files between directories
- [ ] Multi-select and bulk actions
- [ ] File size and upload limits
- [ ] Dockerfile for one-command deployment

---

## Contributing

This is a personal project, but suggestions and improvements are welcome.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

Open an issue first to discuss new features or report bugs.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Author

**Rakib** — Personal project  
🔗 GitHub: https://github.com/YOUR_USERNAME

---

_Made with ❤️ and Flask._
