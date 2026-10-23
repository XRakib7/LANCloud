import mimetypes
import os
import ntpath
import posixpath
import re
import secrets
import shutil
import socket
import stat
import string
import sys
import tempfile
import time
import zipfile
from datetime import datetime

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

IS_WINDOWS = os.name == 'nt'

# On Windows we need ntpath (drive letters, backslashes). On Linux/macOS we
# need posixpath. Keeping the module in one variable makes the path helpers
# explicit and testable.
pathmod = ntpath if IS_WINDOWS else posixpath

# The real OS home. On Termux this is the private app home
# (/data/data/com.termux/files/home), which is not where the user's files live.
SYSTEM_HOME_DIR = pathmod.normpath(pathmod.abspath(os.path.expanduser('~')))
TERMUX_HOME_DIR = SYSTEM_HOME_DIR
APP_DIR = pathmod.normpath(pathmod.abspath(os.path.dirname(__file__)))


def detect_android():
    """True when running under Termux or another Android Python environment."""
    if sys.platform.startswith('android'):
        return True
    if not sys.platform.startswith('linux'):
        return False
    if os.environ.get('TERMUX_VERSION') or 'com.termux' in os.environ.get('PREFIX', ''):
        return True
    if os.path.isdir('/data/data/com.termux/files'):
        return True
    if os.environ.get('ANDROID_ROOT') and os.path.isdir('/storage/emulated/0'):
        return True
    return False


IS_ANDROID = detect_android()
ANDROID_INTERNAL_CANDIDATES = ('/storage/emulated/0', '/sdcard')


def is_readable_dir(path):
    """True if a directory can actually be opened, not just stat()'d."""
    try:
        with os.scandir(path) as entries:
            next(entries, None)
        return True
    except OSError:
        return False


def android_internal_storage():
    """Return the Android shared-storage root (normally /storage/emulated/0)."""
    if not IS_ANDROID:
        return None

    candidates = list(ANDROID_INTERNAL_CANDIDATES)
    candidates.append(os.path.join(TERMUX_HOME_DIR, 'storage', 'shared'))

    fallback = None
    for candidate in candidates:
        try:
            if not os.path.isdir(candidate):
                continue
            real = os.path.realpath(candidate)
            if is_readable_dir(candidate):
                return real
            if fallback is None:
                fallback = real
        except OSError:
            pass
    return fallback


# On Android, "Home" should be shared storage (where photos, Downloads, DCIM
# live), not Termux's private home. Every other OS keeps its normal home.
def default_home_dir():
    if IS_ANDROID:
        internal = android_internal_storage()
        if internal and is_readable_dir(internal):
            return internal
        return TERMUX_HOME_DIR
    return SYSTEM_HOME_DIR


HOME_DIR = default_home_dir()

DRIVE_PATH_RE = re.compile(r'^[A-Za-z]:')
DRIVE_ONLY_RE = re.compile(r'^[A-Za-z]:$')
INVALID_WINDOWS_NAME_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
WINDOWS_RESERVED_NAMES = {
    'CON', 'PRN', 'AUX', 'NUL',
    'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
    'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9',
}

TEXT_EXTENSIONS = {
    '.txt', '.md', '.rst', '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.htm',
    '.css', '.scss', '.less', '.json', '.xml', '.yaml', '.yml', '.toml', '.ini',
    '.cfg', '.conf', '.sh', '.bash', '.zsh', '.env', '.gitignore', '.gitkeep',
    '.csv', '.log', '.sql', '.rb', '.php', '.go', '.rs', '.java', '.c', '.cpp',
    '.h', '.hpp', '.swift', '.kt', '.scala', '.pl', '.lua', '.r', '.m', '.mm',
    '.dockerfile', '.makefile', '.gradle', '.lock', '.patch', '.diff', '.bat',
    '.cmd', '.ps1', '.vbs', '.reg',
}

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff', '.avif'}
ARCHIVE_EXTENSIONS = {'.zip', '.tar', '.gz', '.bz2', '.xz', '.7z', '.rar'}
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.ogg', '.flac', '.aac', '.wma', '.m4a'}
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'}
PDF_EXTENSIONS = {'.pdf'}
CODE_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss', '.less',
    '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.sh',
    '.bash', '.zsh', '.sql', '.rb', '.php', '.go', '.rs', '.java', '.c', '.cpp',
    '.h', '.hpp', '.swift', '.kt', '.scala', '.pl', '.lua', '.r', '.bat',
    '.cmd', '.ps1',
}

# Directory sizes are expensive to calculate (especially C:\Windows or a home
# folder with node_modules). We keep a small time budget per page load instead
# of freezing the page.
SIZE_SCAN_BUDGET = 0.5
SIZE_SCAN_MAX_ENTRIES = 5000


# ---------------------------------------------------------------------------
# Path translation
#
# The browser should never see OS-specific paths. Every link uses a "virtual"
# path made of forward slashes:
#   Linux/macOS:  home/rakib/Documents        (relative to /)
#   Windows:      C:/Users/Rakib/Documents    (includes the drive)
#
# This is what fixes Windows. The old code always assumed '/' meant the root
# of the current drive, which breaks when the project and the home folder are
# on different drives.
# ---------------------------------------------------------------------------

def normalize_virtual(subpath):
    """Return a clean, URL-safe virtual path (no leading slash)."""
    if not subpath:
        return ''

    value = str(subpath).replace('\\', '/').strip()
    value = re.sub(r'/+', '/', value)

    if IS_WINDOWS:
        value = value.lstrip('/')

    parts = []
    for part in value.split('/'):
        if part in ('', '.'):
            continue
        if part == '..':
            # Never pop a drive root ("C:").
            if parts and not DRIVE_ONLY_RE.match(parts[-1]):
                parts.pop()
            continue
        parts.append(part)

    return '/'.join(parts)


def abs_path_from_virtual(subpath):
    """Turn a virtual path into a real absolute OS path."""
    # '/' is used internally by the POSIX root view and by upload forms.
    if subpath == '/':
        return pathmod.normpath(pathmod.abspath(os.sep))

    value = normalize_virtual(subpath)
    if not value:
        return HOME_DIR

    if IS_WINDOWS:
        if DRIVE_ONLY_RE.match(value):
            value += '\\'
        if DRIVE_PATH_RE.match(value):
            return pathmod.normpath(pathmod.abspath(value))

        # A path without a drive is relative to the drive that contains the
        # user's home directory, not to the process's current directory.
        drive = pathmod.splitdrive(HOME_DIR)[0]
        base = drive + pathmod.sep
        return pathmod.normpath(pathmod.abspath(pathmod.join(base, value)))

    return pathmod.normpath(pathmod.abspath('/' + value))


def virtual_path_from_abs(abs_path):
    """Turn a real absolute OS path into a URL-safe virtual path."""
    path = pathmod.normpath(pathmod.abspath(abs_path))

    if IS_WINDOWS:
        drive, rest = pathmod.splitdrive(path)
        rest = rest.replace('\\', '/').strip('/')
        return drive + ('/' + rest if rest else '')

    return path.replace('\\', '/').lstrip('/')


def same_path(first, second):
    return (
        pathmod.normcase(pathmod.normpath(first))
        == pathmod.normcase(pathmod.normpath(second))
    )


def is_drive_root(path):
    if not IS_WINDOWS:
        return False
    drive, tail = pathmod.splitdrive(pathmod.normpath(path))
    return bool(drive) and tail in ('', '/', '\\')


def url_for_dir(abs_path):
    """Build the list-page URL for a directory, including root/drive roots."""
    if same_path(abs_path, HOME_DIR):
        return url_for('index')

    virtual = virtual_path_from_abs(abs_path)
    if virtual:
        return url_for('index', subpath=virtual)

    # POSIX filesystem root. '' means "home", so use ?root instead.
    if IS_ANDROID:
        return url_for('index', root=1, device_root=1)
    return url_for('index', root=1)


def build_breadcrumbs(current_abs, current_virtual):
    """Return crumbs as {name, url}. The last crumb is the current folder."""
    if same_path(current_abs, HOME_DIR):
        return []

    # Inside the home folder: show Home > Documents > Work (not every path
    # component from the drive root).
    try:
        rel = pathmod.relpath(current_abs, HOME_DIR)
    except ValueError:
        rel = None

    if rel is not None and rel != '.':
        rel_parts = [p for p in rel.replace('\\', '/').split('/') if p]
        if '..' not in rel_parts and not pathmod.isabs(rel):
            home_virtual = virtual_path_from_abs(HOME_DIR)
            acc_parts = [p for p in home_virtual.split('/') if p]
            crumbs = []
            for index, part in enumerate(rel_parts):
                acc_parts.append(part)
                acc = '/'.join(acc_parts)
                is_last = index == len(rel_parts) - 1
                crumbs.append({
                    'name': part,
                    'url': None if is_last else url_for('index', subpath=acc),
                })
            return crumbs

    # Outside home: show drive/root and every component.
    parts = [p for p in current_virtual.split('/') if p]
    crumbs = []

    if IS_WINDOWS:
        if parts:
            crumbs.append({
                'name': parts[0],
                'url': None if len(parts) == 1 else url_for('index', subpath=parts[0]),
            })
            start = 1
        else:
            start = 0
    else:
        root_url = (
            url_for('index', root=1, device_root=1)
            if IS_ANDROID
            else url_for('index', root=1)
        )
        crumbs.append({
            'name': 'Root',
            'url': None if not parts else root_url,
        })
        start = 0

    for index in range(start, len(parts)):
        acc = '/'.join(parts[:index + 1])
        is_last = index == len(parts) - 1
        crumbs.append({
            'name': parts[index],
            'url': None if is_last else url_for('index', subpath=acc),
        })

    return crumbs


def is_protected_path(abs_path):
    """Never let the UI delete or rename the home folder or a filesystem root."""
    protected = [HOME_DIR, TERMUX_HOME_DIR, APP_DIR]

    if IS_WINDOWS:
        protected.extend(drive + '\\' for drive in windows_drives())
    else:
        protected.append(pathmod.abspath(os.sep))

    return any(same_path(abs_path, item) for item in protected)


def windows_drives():
    """Return available Windows drive roots such as ['C:', 'D:']."""
    if not IS_WINDOWS:
        return []

    drives = []
    try:
        import ctypes
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        for index in range(26):
            if bitmask & (1 << index):
                drives.append(chr(ord('A') + index) + ':')
    except Exception:
        for letter in string.ascii_uppercase:
            root = letter + ':\\'
            if os.path.exists(root):
                drives.append(letter + ':')

    return drives


def android_storage_roots():
    """Return internal storage plus any SD card / USB storage on Android."""
    if not IS_ANDROID:
        return []

    roots = []

    def add(path):
        try:
            real = os.path.realpath(path)
        except OSError:
            return
        if not os.path.isdir(real):
            return
        if any(same_path(real, existing) for existing in roots):
            return
        roots.append(real)

    for candidate in ANDROID_INTERNAL_CANDIDATES:
        add(candidate)

    # termux-setup-storage creates ~/storage/shared as a link to shared storage.
    add(os.path.join(TERMUX_HOME_DIR, 'storage', 'shared'))

    try:
        for name in sorted(os.listdir('/storage')):
            if name in ('emulated', 'self'):
                continue
            add(os.path.join('/storage', name))
    except OSError:
        pass

    return roots


# ---------------------------------------------------------------------------
# Upload-name sanitising (preserves spaces/unicode, unlike secure_filename)
# ---------------------------------------------------------------------------

def clean_path_component(name):
    name = str(name or '').replace('\x00', '').strip()
    if name in ('', '.', '..'):
        return None

    if IS_WINDOWS:
        name = name.rstrip(' .')
        if not name:
            return None
        name = INVALID_WINDOWS_NAME_RE.sub('_', name)
        stem = name.split('.')[0].upper()
        if stem in WINDOWS_RESERVED_NAMES:
            name = '_' + name
    return name


def clean_upload_filename(name):
    """Keep only the file name; browsers may send C:\\fakepath\\file.txt."""
    value = str(name or '').replace('\\', '/')
    parts = [part for part in value.split('/') if part not in ('', '.')]
    if not parts or '..' in parts:
        return None
    return clean_path_component(parts[-1])


def clean_upload_relative_path(name):
    """Sanitise a browser folder-upload path (Folder/sub/file.txt)."""
    value = str(name or '').replace('\\', '/')
    if value.startswith('/') or DRIVE_PATH_RE.match(value):
        return None

    parts = []
    for part in value.split('/'):
        if part in ('', '.'):
            continue
        if part == '..':
            return None
        cleaned = clean_path_component(part)
        if not cleaned:
            return None
        parts.append(cleaned)
    return parts


def windows_name_error(name):
    """Return a user-facing error for names Windows cannot store."""
    if not IS_WINDOWS:
        return None
    if INVALID_WINDOWS_NAME_RE.search(name):
        return 'That name contains characters Windows does not allow: < > : " / \\ | ? *'
    if name.rstrip(' .') != name:
        return 'Windows does not allow names ending with a space or a dot'
    if name.split('.')[0].upper() in WINDOWS_RESERVED_NAMES:
        return 'That name is reserved by Windows (e.g. CON, NUL, COM1)'
    return None


# ---------------------------------------------------------------------------
# Misc helpers
# ---------------------------------------------------------------------------

def format_size(size_bytes):
    if size_bytes is None:
        return '\u2014'
    if size_bytes < 1024:
        return f'{size_bytes} B'
    if size_bytes < 1024 * 1024:
        return f'{size_bytes / 1024:.1f} KB'
    if size_bytes < 1024 * 1024 * 1024:
        return f'{size_bytes / (1024 * 1024):.1f} MB'
    return f'{size_bytes / (1024 * 1024 * 1024):.2f} GB'


def is_redirected_dir(path):
    """True for symlinks and Windows junctions/reparse points."""
    if os.path.islink(path):
        return True
    try:
        if os.path.isjunction(path):
            return True
    except AttributeError:
        pass
    try:
        attrs = os.stat(path, follow_symlinks=False).st_file_attributes
        return bool(attrs & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    except (AttributeError, OSError):
        return False


def get_dir_size(path, deadline=None, max_entries=SIZE_SCAN_MAX_ENTRIES):
    """Return a folder size, or None when the scan would be too expensive."""
    total = 0
    count = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path, followlinks=False):
            if deadline is not None and time.monotonic() >= deadline:
                return None

            # Do not walk into junctions/symlinks (avoids loops on Windows).
            dirnames[:] = [
                name for name in dirnames
                if not is_redirected_dir(os.path.join(dirpath, name))
            ]

            for filename in filenames:
                try:
                    total += os.path.getsize(os.path.join(dirpath, filename))
                except OSError:
                    pass
                count += 1
                if count >= max_entries:
                    return None
    except OSError:
        pass
    return total


def get_file_type(filename, is_dir):
    if is_dir:
        return 'Folder'
    ext = os.path.splitext(filename)[1].lower()
    if ext in TEXT_EXTENSIONS:
        return 'Text'
    if ext in IMAGE_EXTENSIONS:
        return 'Image'
    if ext in PDF_EXTENSIONS:
        return 'PDF'
    if ext in ARCHIVE_EXTENSIONS:
        return 'Archive'
    if ext in AUDIO_EXTENSIONS:
        return 'Audio'
    if ext in VIDEO_EXTENSIONS:
        return 'Video'
    if ext in CODE_EXTENSIONS:
        return 'Code'
    return 'File'


def is_text_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext in TEXT_EXTENSIONS or ext in CODE_EXTENSIONS:
        return True
    guessed = mimetypes.guess_type(filename)[0]
    return bool(guessed and guessed.startswith('text/'))


def make_item(name, item_path, is_dir, deadline, is_drive=False):
    virtual = virtual_path_from_abs(item_path)
    modified = None
    stat_result = None

    try:
        stat_result = os.stat(item_path)
        modified = datetime.fromtimestamp(stat_result.st_mtime)
    except (OSError, ValueError, OverflowError):
        pass

    if is_drive:
        size_value = 0
        size_text = '\u2014'
        try:
            usage = shutil.disk_usage(item_path)
            size_value = usage.total
            size_text = f'{format_size(usage.free)} free'
        except OSError:
            pass
        file_type = 'Drive'
        is_text = False
    elif is_dir:
        size_value = 0
        size_text = '\u2014'
        computed = get_dir_size(item_path, deadline=deadline)
        if computed is not None:
            size_value = computed
            size_text = format_size(computed)
        file_type = 'Folder'
        is_text = False
    else:
        size_value = stat_result.st_size if stat_result is not None else 0
        size_text = format_size(stat_result.st_size) if stat_result is not None else '\u2014'
        file_type = get_file_type(name, False)
        is_text = is_text_file(name)

    item = {
        'name': name,
        'path': virtual,
        'is_dir': is_dir,
        'is_drive': is_drive,
        'size': size_value,
        'size_display': size_text,
        'modified': modified.strftime('%Y-%m-%d %H:%M') if modified else '\u2014',
        'modified_sort': modified.timestamp() if modified else 0,
        'file_type': file_type,
        'is_text': is_text,
        'url': (
            url_for('index', subpath=virtual)
            if is_dir else url_for('download', filename=virtual)
        ),
        'download_url': url_for('download', filename=virtual),
        'edit_url': url_for('edit', filename=virtual) if is_text and not is_dir else None,
        'rename_url': None if is_drive else url_for('rename', filename=virtual),
        'delete_url': None if is_drive else url_for('delete', filename=virtual),
    }
    return item


def make_shortcut_item(name, abs_path, url, file_type='Folder'):
    """Build a row for a navigation shortcut (storage roots, home, etc.)."""
    size_value = 0
    size_text = '\u2014'
    try:
        usage = shutil.disk_usage(abs_path)
        size_value = usage.total
        size_text = f'{format_size(usage.free)} free'
    except OSError:
        pass

    return {
        'name': name,
        'path': virtual_path_from_abs(abs_path),
        'is_dir': True,
        'is_drive': False,
        'size': size_value,
        'size_display': size_text,
        'modified': '\u2014',
        'modified_sort': 0,
        'file_type': file_type,
        'is_text': False,
        'url': url,
        'download_url': None,
        'edit_url': None,
        'rename_url': None,
        'delete_url': None,
    }


def redirect_to_dir(abs_path):
    return redirect(url_for_dir(abs_path))


def render_android_storage():
    """Android-only storage overview shown by the globe/root button."""
    internal = android_internal_storage()
    items = []

    for path in android_storage_roots():
        if internal and same_path(path, internal):
            name = 'Internal storage (0)'
            file_type = 'Internal storage'
        else:
            name = f'SD card / USB ({os.path.basename(path)})'
            file_type = 'Removable storage'
        items.append(make_shortcut_item(
            name,
            path,
            url_for('index', subpath=virtual_path_from_abs(path)),
            file_type,
        ))

    items.append(make_shortcut_item(
        'Termux home',
        TERMUX_HOME_DIR,
        url_for('index', subpath=virtual_path_from_abs(TERMUX_HOME_DIR)),
        'Folder',
    ))
    items.append(make_shortcut_item(
        'Device root (/)',
        pathmod.abspath(os.sep),
        url_for('index', root=1, device_root=1),
        'System',
    ))

    return render_template(
        'index.html',
        items=items,
        current_path='',
        form_path='',
        current_abs_path='Storage',
        parent_url=None,
        breadcrumbs=[{'name': 'Storage', 'url': None}],
        at_home=False,
        drive_view=True,
    )


@app.context_processor
def inject_android_helpers():
    internal = android_internal_storage()
    return {
        'is_android': IS_ANDROID,
        'android_internal_url': (
            url_for('index', subpath=virtual_path_from_abs(internal))
            if internal else None
        ),
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route('/favicon.ico')
def favicon():
    return '', 204


@app.route('/')
@app.route('/<path:subpath>')
def index(subpath=''):
    show_device_root = 'device_root' in request.args
    show_root = 'root' in request.args or show_device_root

    # On Android, the globe button opens a storage overview instead of the
    # Linux / directory (which mostly contains Termux internals).
    if show_root and IS_ANDROID and not show_device_root:
        return render_android_storage()

    drive_view = False

    if show_root:
        if IS_WINDOWS:
            drive_view = True
            target_abs = None
            current_virtual = ''
            form_path = ''
        else:
            target_abs = pathmod.normpath(pathmod.abspath(os.sep))
            current_virtual = ''
            form_path = '/'
    else:
        current_virtual = normalize_virtual(subpath)
        target_abs = abs_path_from_virtual(current_virtual)
        form_path = current_virtual

    items = []

    if drive_view:
        deadline = time.monotonic() + SIZE_SCAN_BUDGET
        for drive in windows_drives():
            items.append(make_item(drive + pathmod.sep, drive + pathmod.sep, True, deadline, is_drive=True))

        return render_template(
            'index.html',
            items=items,
            current_path=form_path,
            form_path=form_path,
            current_abs_path='This PC',
            parent_url=None,
            breadcrumbs=[{'name': 'This PC', 'url': None}],
            at_home=False,
            drive_view=True,
        )

    if not os.path.exists(target_abs):
        flash(f'Path not found: {current_virtual or target_abs}', 'error')
        return redirect(url_for('index'))

    if not os.path.isdir(target_abs):
        flash('That path is not a folder', 'error')
        parent = pathmod.dirname(target_abs)
        if same_path(parent, target_abs):
            return redirect(url_for('index'))
        return redirect_to_dir(parent)

    deadline = time.monotonic() + SIZE_SCAN_BUDGET

    try:
        names = sorted(os.listdir(target_abs), key=lambda name: name.lower())
    except OSError as exc:
        names = []
        if IS_ANDROID:
            flash('Cannot open this folder. Run "termux-setup-storage" in Termux, allow storage access, then try again.', 'error')
        else:
            flash(f'Cannot open this folder: {exc.strerror or exc}', 'error')

    for name in names:
        item_path = pathmod.join(target_abs, name)
        try:
            is_dir = os.path.isdir(item_path)
        except OSError:
            is_dir = False
        items.append(make_item(name, item_path, is_dir, deadline))

    items.sort(key=lambda item: (not item['is_dir'], item['name'].lower()))

    parent_url = None
    parent_abs = pathmod.dirname(target_abs)
    if not same_path(parent_abs, target_abs):
        parent_url = url_for_dir(parent_abs)

    at_home = same_path(target_abs, HOME_DIR)

    return render_template(
        'index.html',
        items=items,
        current_path=form_path,
        form_path=form_path,
        current_abs_path=target_abs,
        parent_url=parent_url,
        breadcrumbs=build_breadcrumbs(target_abs, current_virtual),
        at_home=at_home,
        drive_view=False,
    )


@app.route('/upload', methods=['POST'])
def upload():
    target_path = request.form.get('target_path', '')
    safe_path = abs_path_from_virtual(target_path)

    if not os.path.isdir(safe_path):
        flash('Invalid target directory', 'error')
        return redirect(url_for('index'))

    files = request.files.getlist('file')
    if not files:
        flash('No file selected', 'error')
        return redirect_to_dir(safe_path)

    uploaded = 0
    for uploaded_file in files:
        if not uploaded_file.filename:
            continue

        filename = clean_upload_filename(uploaded_file.filename)
        if not filename:
            flash(f'Skipped a file with an invalid name: {uploaded_file.filename}', 'error')
            continue

        destination = pathmod.join(safe_path, filename)
        try:
            uploaded_file.save(destination)
            uploaded += 1
        except OSError as exc:
            flash(f'Error uploading {filename}: {exc}', 'error')

    if uploaded:
        flash(f'{uploaded} file(s) uploaded successfully', 'success')

    return redirect_to_dir(safe_path)


@app.route('/upload_folder', methods=['POST'])
def upload_folder():
    target_path = request.form.get('target_path', '')
    safe_path = abs_path_from_virtual(target_path)

    if not os.path.isdir(safe_path):
        flash('Invalid target directory', 'error')
        return redirect(url_for('index'))

    files = request.files.getlist('folder')
    if not files:
        flash('No folder selected', 'error')
        return redirect_to_dir(safe_path)

    count = 0
    for uploaded_file in files:
        if not uploaded_file.filename:
            continue

        parts = clean_upload_relative_path(uploaded_file.filename)
        if not parts:
            flash(f'Skipped an unsafe path: {uploaded_file.filename}', 'error')
            continue

        destination = pathmod.join(safe_path, *parts)
        try:
            parent = pathmod.dirname(destination)
            if parent:
                os.makedirs(parent, exist_ok=True)
            uploaded_file.save(destination)
            count += 1
        except OSError as exc:
            flash(f'Error saving {"/".join(parts)}: {exc}', 'error')

    if count:
        flash(f'Folder uploaded ({count} files)', 'success')

    return redirect_to_dir(safe_path)


@app.route('/download/<path:filename>')
def download(filename):
    safe_path = abs_path_from_virtual(filename)

    if not os.path.exists(safe_path):
        flash('File not found', 'error')
        return redirect(url_for('index'))

    if os.path.isdir(safe_path):
        return download_folder(safe_path)

    try:
        return send_file(safe_path, as_attachment=True, download_name=os.path.basename(safe_path))
    except OSError as exc:
        flash(f'Cannot download this file: {exc}', 'error')
        return redirect_to_dir(pathmod.dirname(safe_path))


def _remove_quietly(path):
    try:
        os.unlink(path)
    except OSError:
        pass


def download_folder(safe_path):
    if not os.path.isdir(safe_path):
        flash('Folder not found', 'error')
        return redirect(url_for('index'))

    temp_file = tempfile.NamedTemporaryFile(prefix='lancloud_', suffix='.zip', delete=False)
    temp_name = temp_file.name
    temp_file.close()
    temp_norm = os.path.normcase(os.path.abspath(temp_name))

    try:
        with zipfile.ZipFile(temp_name, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as archive:
            for root, dirs, files in os.walk(safe_path):
                dirs[:] = [name for name in dirs if not is_redirected_dir(os.path.join(root, name))]
                for name in files:
                    full_path = os.path.join(root, name)
                    # The ZIP itself can live inside the folder being zipped
                    # (Windows temp is under C:\Users\...). Never include it.
                    if os.path.normcase(os.path.abspath(full_path)) == temp_norm:
                        continue
                    arcname = os.path.relpath(full_path, safe_path).replace('\\', '/')
                    try:
                        archive.write(full_path, arcname)
                    except OSError:
                        pass
    except OSError as exc:
        _remove_quietly(temp_name)
        flash(f'Could not create ZIP: {exc}', 'error')
        return redirect_to_dir(safe_path)

    clean_path = safe_path.rstrip('/\\')
    folder_name = pathmod.basename(clean_path)
    if not folder_name:
        drive = pathmod.splitdrive(clean_path)[0].replace(':', '')
        folder_name = f'{drive}_drive' if drive else 'folder'

    response = send_file(
        temp_name,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'{folder_name}.zip',
    )
    response.call_on_close(lambda: _remove_quietly(temp_name))
    return response


@app.route('/delete/<path:filename>', methods=['POST'])
def delete(filename):
    safe_path = abs_path_from_virtual(filename)

    if is_protected_path(safe_path):
        flash('Refusing to delete a protected system location', 'error')
        return redirect(url_for('index'))

    if not os.path.exists(safe_path):
        flash('File or directory not found', 'error')
        return redirect(url_for('index'))

    try:
        if os.path.isfile(safe_path) or os.path.islink(safe_path):
            os.remove(safe_path)
            flash(f'Deleted: {os.path.basename(safe_path)}', 'success')
        elif os.path.isdir(safe_path):
            shutil.rmtree(safe_path)
            flash(f'Deleted folder: {os.path.basename(safe_path)}', 'success')
        else:
            flash('File or directory not found', 'error')
    except OSError as exc:
        flash(f'Error deleting: {exc}', 'error')

    parent = pathmod.dirname(safe_path)
    if same_path(parent, safe_path):
        return redirect(url_for('index'))
    return redirect_to_dir(parent)


@app.route('/rename/<path:filename>', methods=['GET', 'POST'])
def rename(filename):
    safe_path = abs_path_from_virtual(filename)

    if not os.path.exists(safe_path):
        flash('File or directory not found', 'error')
        return redirect(url_for('index'))

    if is_protected_path(safe_path):
        flash('Refusing to rename a protected system location', 'error')
        return redirect(url_for('index'))

    current_name = os.path.basename(safe_path.rstrip('/\\')) or safe_path
    parent_dir = pathmod.dirname(safe_path)
    parent_url = url_for_dir(parent_dir)

    if request.method == 'POST':
        new_name = request.form.get('new_name', '').strip()

        if not new_name:
            flash('New name is required', 'error')
            return redirect(request.url)

        if new_name in ('.', '..') or '/' in new_name or '\\' in new_name:
            flash('A name cannot contain / or \\', 'error')
            return redirect(request.url)

        name_error = windows_name_error(new_name)
        if name_error:
            flash(name_error, 'error')
            return redirect(request.url)

        new_path = pathmod.join(parent_dir, new_name)
        if not same_path(pathmod.dirname(new_path), parent_dir):
            flash('Invalid new name', 'error')
            return redirect(request.url)

        try:
            os.rename(safe_path, new_path)
            flash(f'Renamed to {new_name}', 'success')
            return redirect_to_dir(parent_dir)
        except OSError as exc:
            flash(f'Error renaming: {exc}', 'error')
            return redirect(request.url)

    return render_template(
        'rename.html',
        filename=virtual_path_from_abs(safe_path),
        current_name=current_name,
        parent_url=parent_url,
        breadcrumbs=build_breadcrumbs(safe_path, virtual_path_from_abs(safe_path)),
        at_home=False,
    )


@app.route('/edit/<path:filename>', methods=['GET', 'POST'])
def edit(filename):
    safe_path = abs_path_from_virtual(filename)

    if not os.path.isfile(safe_path):
        flash('File not found', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        new_content = request.form.get('content', '')
        try:
            with open(safe_path, 'w', encoding='utf-8', errors='replace', newline='') as handle:
                handle.write(new_content)
            flash('File saved successfully', 'success')
            return redirect_to_dir(pathmod.dirname(safe_path))
        except OSError as exc:
            flash(f'Error saving file: {exc}', 'error')

    try:
        with open(safe_path, 'r', encoding='utf-8', errors='replace', newline='') as handle:
            content = handle.read()
    except OSError as exc:
        flash(f'Error reading file: {exc}', 'error')
        return redirect(url_for('index'))

    virtual = virtual_path_from_abs(safe_path)
    return render_template(
        'edit.html',
        filename=virtual,
        display_name=os.path.basename(safe_path),
        content=content,
        parent_url=url_for_dir(pathmod.dirname(safe_path)),
        breadcrumbs=build_breadcrumbs(safe_path, virtual),
        at_home=False,
    )


@app.route('/new_folder', methods=['POST'])
def new_folder():
    folder_name = request.form.get('folder_name', '').strip()
    target_path = request.form.get('target_path', '')
    safe_path = abs_path_from_virtual(target_path)

    if not os.path.isdir(safe_path):
        flash('Invalid target directory', 'error')
        return redirect(url_for('index'))

    if not folder_name:
        flash('Folder name is required', 'error')
        return redirect_to_dir(safe_path)

    if folder_name in ('.', '..') or '/' in folder_name or '\\' in folder_name:
        flash('A folder name cannot contain / or \\', 'error')
        return redirect_to_dir(safe_path)

    name_error = windows_name_error(folder_name)
    if name_error:
        flash(name_error, 'error')
        return redirect_to_dir(safe_path)

    new_path = pathmod.join(safe_path, folder_name)
    try:
        os.mkdir(new_path)
        flash(f'Folder "{folder_name}" created', 'success')
    except FileExistsError:
        flash('Folder already exists', 'error')
    except OSError as exc:
        flash(f'Error: {exc}', 'error')

    return redirect_to_dir(safe_path)


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

def get_lan_ip():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.connect(('8.8.8.8', 80))
            return sock.getsockname()[0]
        finally:
            sock.close()
    except OSError:
        try:
            return socket.gethostbyname(socket.gethostname())
        except OSError:
            return '127.0.0.1'


def get_port():
    try:
        return int(os.environ.get('PORT', '5000'))
    except ValueError:
        return 5000


if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = get_port()
    debug = os.environ.get('FLASK_DEBUG', '').lower() in ('1', 'true', 'yes', 'on')
    lan_ip = get_lan_ip()

    print('LANCloud is running:')
    print(f'  Local:   http://127.0.0.1:{port}')
    print(f'  Network: http://{lan_ip}:{port}')
    print(f'  Home:    {HOME_DIR}')
    if IS_ANDROID and not same_path(HOME_DIR, TERMUX_HOME_DIR):
        print(f'  Termux:  {TERMUX_HOME_DIR}  (globe button -> Termux home)')
    print(f'  Root:    {"This PC (all drives)" if IS_WINDOWS else "/"}')
    if IS_WINDOWS:
        print('  Tip:     If other devices cannot connect, allow Python through')
        print('           Windows Firewall on Private networks (see README).')
    print('  Stop:    Ctrl+C')

    app.run(host=host, port=port, debug=debug)
