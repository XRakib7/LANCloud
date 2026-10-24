# LANCloud

A small Flask app that serves your filesystem as a web file manager over your local network. Run it on a PC, laptop, VM or phone, then open it from any other device on the same WiFi to browse, upload, download and edit files without cables or cloud storage.

It's a single Python file plus a few templates. No database, no accounts, nothing leaves your network.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- Browse the whole filesystem with breadcrumb navigation. On Windows you can switch between drives.
- Upload single files or an entire folder with its subdirectories.
- Download a file, or download a folder as a ZIP.
- Edit text files directly in the browser.
- Create folders, rename, and delete (with confirmation).
- Live search as you type, and sortable columns.
- Dark mode that is remembered between visits.
- Responsive layout, usable from a phone.

## Requirements

- Python 3.8 or newer
- A web browser on the device you're browsing from

Nothing else. No Node.js, no Docker, no config file.

## Setup

```bash
git clone https://github.com/XRakib7/LANCloud.git
cd LANCloud
python -m pip install -r requirements.txt
python app.py
```

On Windows use the launcher instead of `python`:

```bat
py -m pip install -r requirements.txt
py app.py
```

`requirements.txt` asks for `Flask>=2.3,<4`, so pip will pick a version that matches your Python.

There are also two launcher scripts that install Flask if it's missing:

- Windows: `run_windows.bat`
- Linux/macOS: `./run_linux.sh`

On startup the app prints something like this:

```
LANCloud is running:
  Local:   http://127.0.0.1:5000
  Network: http://192.168.1.10:5000
  Home:    /home/yourname
  Root:    /
```

Open the Local address on the same machine, or the Network address from your phone or another computer.

## Windows

Windows blocks incoming connections by default, which is the usual reason the app opens on the PC but not on your phone. You need to allow the port through the firewall.

The quickest way is to right-click `allow_firewall_windows.bat` and choose **Run as administrator**. Then check that your WiFi network is set to **Private** (Settings → Network & Internet → WiFi → your network → Network profile type).

To add the rule manually, open Command Prompt as Administrator:

```bat
netsh advfirewall firewall add rule name="LANCloud" dir=in action=allow protocol=TCP localport=5000 profile=private,domain
```

To remove it later:

```bat
netsh advfirewall firewall delete rule name="LANCloud"
```

To find your IP address:

```bat
ipconfig
```

Look for the IPv4 address under your active WiFi or Ethernet adapter, then open `http://192.168.1.107:5000` (with your own address).

The globe button next to the home button opens **This PC** with all available drives, so you can browse `C:`, `D:`, USB drives and so on even if the project lives on a different drive than your home folder.

If another device still can't connect:

- Both devices must be on the same WiFi network, not mobile data or a guest network.
- Turn off any VPN on either device while testing.
- Some routers isolate clients from each other. Turn that off for your home network.
- Check that the Flask window is still running and shows `Running on http://0.0.0.0:5000`.
- Test the `127.0.0.1` URL on the PC first. If that works but the LAN address doesn't, it's the firewall or the network profile.

## Android (Termux)

Android can host LANCloud through Termux:

```bash
pkg update && pkg install python
termux-setup-storage
cd ~/LANCloud
python -m pip install -r requirements.txt
python app.py
```

`termux-setup-storage` is the important step, since it gives Termux access to shared storage.

On Android, the Home button opens `/storage/emulated/0` by default. The phone button in the header jumps straight there from anywhere, and the globe button lists internal storage, any SD card or USB storage, the Termux home directory, and the device root.

If Android stops the server when the screen locks, run `termux-wake-lock` before starting it.

Folder upload depends on the browser. Browsing, downloading, uploading files, editing, renaming and deleting all work normally.

## Usage

| Action | How |
|---|---|
| Browse | Click a folder to open it, `..` to go up, or use the breadcrumb trail |
| Switch drives (Windows) | Globe button → **This PC** |
| Open phone storage (Android) | Home opens internal storage, the phone button is a shortcut, the globe button lists all storage |
| Upload a file | **Upload File**, one or many |
| Upload a folder | **Upload Folder**, structure is preserved |
| Download a file | Download icon next to the file |
| Download a folder | Download icon next to the folder, delivered as a ZIP |
| Edit a text file | Pencil icon, then **Save Changes** |
| Rename | Rename icon, enter a new name |
| Delete | Trash icon, then confirm. This is permanent. |
| Create a folder | **New Folder** |
| Search | Type in the search box, the list filters live |
| Sort | Click a column header |
| Dark mode | Toggle the theme switch |

The app starts in your home directory, but the globe/root button lets you reach the rest of the filesystem, which is handy for editing system configs on a VM or opening another Windows drive.

Folder sizes are calculated with a time budget so that opening something like `C:\Windows` doesn't hang the page. Folders that take too long to scan show `—` instead of a size.

## VirtualBox

Getting files into and out of a VM without configuring Samba or shared folders is one of the more useful ways to run this.

Bridged adapter, recommended:

1. VM Settings → Network → Attach to **Bridged Adapter**
2. Start the VM; it gets its own IP on your network
3. Open `http://<VM-IP>:5000` from the host or your phone

NAT with port forwarding:

1. VM Settings → Network → Attach to **NAT Network** → Port Forwarding, then add:

   | Protocol | Host IP | Host Port | Guest Port |
   |---|---|---|---|
   | TCP | 127.0.0.1 | 5000 | 5000 |

2. Allow the port inside the VM:

   ```bash
   sudo ufw allow 5000/tcp
   ```

3. Open `http://127.0.0.1:5000` on the host.

## Troubleshooting

**`pip install -r requirements.txt` can't find Flask**

Use the pip that belongs to your Python (`py -m pip` on Windows, `python3 -m pip` on Linux/macOS). Upgrading pip with `python -m pip install --upgrade pip` usually helps. Check `python --version` is 3.8 or newer.

**The page loads on the PC but not on my phone**

See the Windows section above. On Linux, run `sudo ufw allow 5000/tcp`.

**`Address already in use`**

Something else is using port 5000, or a previous instance is still running. Use a different port:

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

Then open `http://<your-ip>:8080`. If you use the firewall script, pass the same port to it.

**A page shows "Internal Server Error"**

Run the app from a terminal and read the traceback. The usual causes are permission-protected folders and files locked by another program. Most of these are caught and shown as a flash message rather than crashing the app.

**`C:\Windows` or a large folder feels slow**

Only the size column is slow, and it's intentionally capped. The listing itself is quick, and opening, downloading, renaming and deleting still work.

## Security

There is no login. Anyone on your network who knows the address can read and write files, which is the intended behaviour for a home network tool but worth being explicit about.

Reasonable for a home WiFi network, a trusted VM, or quick transfers between your own devices. Don't run it on public WiFi, on a network with people you don't trust, or port-forwarded to the internet.

If you need to lock it down:

- Set a fixed secret key so sessions survive a restart: `SECRET_KEY=your-long-random-value` (or `set SECRET_KEY=...` on Windows).
- Bind to localhost only: `HOST=127.0.0.1 python app.py`.
- Put it behind an authenticating reverse proxy such as Nginx if it has to be reachable from outside.
- Debug mode is off by default. Enable it only locally with `FLASK_DEBUG=1 python app.py`.

## Configuration

| Variable | Default | Notes |
|---|---|---|
| `PORT` | `5000` | Port to listen on |
| `HOST` | `0.0.0.0` | Use `127.0.0.1` for local-only access |
| `SECRET_KEY` | random per start | Set it to keep sessions between restarts |
| `FLASK_DEBUG` | off | Development only |

Theme colours and file-type icons live in the templates.

## Roadmap

- [ ] Login/password protection
- [ ] Image, video and PDF previews
- [ ] Copy and move files between directories
- [ ] Multi-select and bulk actions
- [ ] Drag-and-drop uploads
- [ ] Dockerfile

## Contributing

Pull requests and suggestions are welcome.

1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature`
3. Commit your change
4. Push and open a pull request

For bugs, open an issue first so we can work out what's going on.

## License

MIT. See [LICENSE](LICENSE).

## Author

XRakib7 — https://github.com/XRakib7
