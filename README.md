# LANCloud

A small Flask app that serves your filesystem as a web file manager over your local network. Run it on a PC, laptop, VM or phone, then open it from any other device on the same WiFi to browse, upload, download and edit files without cables or cloud storage.

It's a single Python file plus a few templates. No database, no accounts, nothing leaves your network.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- Browse the whole filesystem with breadcrumb navigation. On Windows you can switch between drives.
- Upload single files or an entire folder with its subdirectories.
- Large uploads are sent in resumable chunks with live speed/progress, so a dropped WiFi connection can retry from the last byte instead of starting over.
- Drag and drop files or folders straight into the page.
- Download a file with HTTP Range support (browsers and download managers can pause and resume), or download a folder as a ZIP streamed on the fly.
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
| Upload a folder | **Upload Folder**, or drag a folder onto the page. Structure is preserved |
| Cancel/retry an upload | The transfer panel shows **Cancel**; after a network error, **Retry** resumes from where the server stopped |
| Download a file | Download icon next to the file. Large files can be paused/resumed by the browser |
| Download a folder | Download icon next to the folder, delivered as a ZIP streamed on the fly |
| Edit a text file | Pencil icon, then **Save Changes** |
| Rename | Rename icon, enter a new name |
| Delete | Trash icon, then confirm. This is permanent. |
| Create a folder | **New Folder** |
| Search | Type in the search box, the list filters live |
| Sort | Click a column header |
| Dark mode | Toggle the theme switch |

The app starts in your home directory, but the globe/root button lets you reach the rest of the filesystem, which is handy for editing system configs on a VM or opening another Windows drive.

Folder sizes are calculated with a time budget so that opening something like `C:\Windows` doesn't hang the page. Folders that take too long to scan show `—` instead of a size.

## Large transfers

Uploads do not go through one giant form POST. The browser splits each file into 8 MB chunks and the server appends them to a temporary `.part` file. While a transfer is running, a panel in the bottom-right corner shows progress and speed. If the connection drops, the uploader asks the server how many bytes it already has and continues from there. The same panel lets you cancel a transfer, retry a failed one, or clear finished entries.

A few details worth knowing:

- Keep the browser tab open while an upload runs. The file handle lives in the page, so closing or reloading the tab ends the transfer.
- The chunk size is `UPLOAD_CHUNK_SIZE` near the top of `app.py` (8 MB by default). Increase it only if you have plenty of RAM on both devices; decrease it on a slow or unstable link.
- Unfinished parts live in the system temp folder (`lancloud-uploads`) and are cleaned up after 24 hours. You can delete that folder while the app is stopped if you want the space back sooner.
- File downloads use HTTP Range requests, so a browser or download manager can resume a large file. Folder downloads are a ZIP stream: they start immediately and need no extra disk space, but they cannot be resumed.
- On Android, pick local files with the **Files** app (for example from **Downloads** or **DCIM**). Files opened from Google Drive, Photos or other cloud providers can arrive as unreadable placeholders. The uploader now stops with a clear message instead of creating a 0-byte file; copy the file to the phone first and try again.
- On Android, run `termux-wake-lock` before a long transfer so Android does not suspend Termux.

If you put LANCloud behind Nginx or another reverse proxy, allow chunk-sized request bodies (16 MB is plenty with the default chunk size) and give uploads a generous read timeout. The built-in Flask server does not need any extra configuration.

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

**A big upload from Android finishes immediately and leaves a 0-byte file**

This is an Android file-picker problem, not a LANCloud problem. Some providers (Google Drive, Photos, cloud file managers) give the browser a file handle that reports `0 B` and cannot be read. The page used to trust that value and complete an empty upload. It now refuses and explains what to do:

1. Download or copy the file into the phone's own storage, such as `Download` or `DCIM`.
2. In Chrome's file picker, choose **Files** (not Drive/Photos) and open it from there.
3. If the picker still shows `0 B`, transfer that particular file with a USB cable, MTP, or `adb push` instead. No web page can read a file the browser itself cannot open.

The server also rejects a chunked upload whose size is 0 unless the page explicitly confirms that the file is genuinely empty, so a failed Android pick can no longer create a silent 0-byte file.

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
- [ ] Resume uploads after closing the tab
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
