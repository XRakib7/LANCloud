import os
import shutil
import zipfile
import io
import mimetypes
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, send_file

app = Flask(__name__)
app.secret_key = 'filemanager-secret-key-change-in-production'
BASE_DIR = '/'
HOME_DIR = os.path.expanduser('~')

TEXT_EXTENSIONS = {
    '.txt', '.md', '.rst', '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.htm',
    '.css', '.scss', '.less', '.json', '.xml', '.yaml', '.yml', '.toml', '.ini',
    '.cfg', '.conf', '.sh', '.bash', '.zsh', '.env', '.gitignore', '.gitkeep',
    '.csv', '.log', '.sql', '.rb', '.php', '.go', '.rs', '.java', '.c', '.cpp',
    '.h', '.hpp', '.swift', '.kt', '.scala', '.pl', '.lua', '.r', '.m', '.mm',
    '.dockerfile', '.makefile', '.gradle', '.lock', '.patch', '.diff',
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
    '.h', '.hpp', '.swift', '.kt', '.scala', '.pl', '.lua', '.r',
}


def format_size(size_bytes):
    if size_bytes < 1024:
        return f'{size_bytes} B'
    elif size_bytes < 1024 * 1024:
        return f'{size_bytes / 1024:.1f} KB'
    elif size_bytes < 1024 * 1024 * 1024:
        return f'{size_bytes / (1024 * 1024):.1f} MB'
    else:
        return f'{size_bytes / (1024 * 1024 * 1024):.2f} GB'


def get_dir_size(path):
    total = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                try:
                    fp = os.path.join(dirpath, f)
                    total += os.path.getsize(fp)
                except OSError:
                    pass
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
    mt = mimetypes.guess_type(filename)[0]
    if mt and mt.startswith('text/'):
        return True
    return False


def get_safe_path(subpath):
    if subpath is None or subpath == '':
        return HOME_DIR
    full_path = os.path.abspath('/' + subpath.lstrip('/'))
    return full_path


def get_relative_path(abs_path):
    rel = os.path.relpath(abs_path, '/')
    if rel == '.':
        return ''
    return rel


@app.route('/')
@app.route('/<path:subpath>')
def index(subpath=''):
    if 'root' in request.args:
        safe_path = '/'
    else:
        safe_path = get_safe_path(subpath)
    if safe_path is None or not os.path.exists(safe_path):
        flash('Invalid path', 'error')
        return redirect(url_for('index'))

    items = []
    try:
        for item in sorted(os.listdir(safe_path), key=lambda x: x.lower()):
            item_path = os.path.join(safe_path, item)
            is_dir = os.path.isdir(item_path)
            rel_path = os.path.relpath(item_path, '/')
            try:
                st = os.stat(item_path)
                modified = datetime.fromtimestamp(st.st_mtime)
            except OSError:
                modified = datetime.now()

            if is_dir:
                dir_size = get_dir_size(item_path)
                size_val = dir_size
                size_text = format_size(dir_size) if dir_size > 0 else '0 B'
            else:
                size_val = st.st_size
                size_text = format_size(st.st_size)

            items.append({
                'name': item,
                'path': rel_path,
                'is_dir': is_dir,
                'size': size_val,
                'size_display': size_text,
                'modified': modified.strftime('%Y-%m-%d %H:%M'),
                'modified_sort': modified.timestamp(),
                'file_type': get_file_type(item, is_dir),
                'is_text': is_text_file(item) if not is_dir else False,
            })
    except PermissionError:
        flash('Permission denied for this directory', 'error')

    items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))

    # Build breadcrumb trail
    breadcrumbs = []
    if subpath:
        parts = subpath.split('/')
        acc = ''
        for p in parts:
            acc = os.path.join(acc, p) if acc else p
            breadcrumbs.append({'name': p, 'path': acc})

    # No parent when at home page (showing HOME_DIR)
    if not subpath:
        parent_path = None
    else:
        parent_abs = os.path.dirname('/' + subpath.rstrip('/').lstrip('/'))
        if parent_abs == '/':
            parent_path = ''
        else:
            parent_path = parent_abs.lstrip('/')

    return render_template('index.html',
                           items=items,
                           current_path=subpath or '',
                           parent_path=parent_path,
                           current_abs_path=safe_path,
                           breadcrumbs=breadcrumbs)


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(request.referrer or url_for('index'))

    files = request.files.getlist('file')
    target_path = request.form.get('target_path', '')
    safe_path = get_safe_path(target_path)
    if safe_path is None or not os.path.isdir(safe_path):
        flash('Invalid target directory', 'error')
        return redirect(request.referrer or url_for('index'))

    uploaded = 0
    for f in files:
        if f.filename == '':
            continue
        try:
            f.save(os.path.join(safe_path, f.filename))
            uploaded += 1
        except Exception as e:
            flash(f'Error uploading {f.filename}: {str(e)}', 'error')

    if uploaded > 0:
        flash(f'{uploaded} file(s) uploaded successfully', 'success')

    return redirect(url_for('index', subpath=target_path) if target_path else url_for('index'))


@app.route('/upload_folder', methods=['POST'])
def upload_folder():
    if 'folder' not in request.files:
        flash('No folder selected', 'error')
        return redirect(request.referrer or url_for('index'))

    files = request.files.getlist('folder')
    target_path = request.form.get('target_path', '')
    safe_path = get_safe_path(target_path)
    if safe_path is None or not os.path.isdir(safe_path):
        flash('Invalid target directory', 'error')
        return redirect(request.referrer or url_for('index'))

    count = 0
    for f in files:
        if f.filename == '':
            continue
        rel_path = f.filename
        abs_path = os.path.join(safe_path, rel_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        try:
            f.save(abs_path)
            count += 1
        except Exception as e:
            flash(f'Error saving {rel_path}: {str(e)}', 'error')

    if count > 0:
        flash(f'Folder uploaded ({count} files)', 'success')

    return redirect(url_for('index', subpath=target_path) if target_path else url_for('index'))


@app.route('/download/<path:filename>')
def download(filename):
    safe_path = get_safe_path(filename)
    if safe_path is None or not os.path.exists(safe_path):
        flash('File not found', 'error')
        return redirect(url_for('index'))

    if os.path.isdir(safe_path):
        return download_folder(filename)

    directory = os.path.dirname(safe_path)
    basename = os.path.basename(safe_path)
    return send_from_directory(directory, basename, as_attachment=True)


def download_folder(folderpath):
    safe_path = get_safe_path(folderpath)
    if safe_path is None or not os.path.isdir(safe_path):
        flash('Folder not found', 'error')
        return redirect(url_for('index'))

    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(safe_path):
            for f in files:
                fp = os.path.join(root, f)
                arcname = os.path.relpath(fp, safe_path)
                try:
                    zipf.write(fp, arcname)
                except OSError:
                    pass

    memory_file.seek(0)
    folder_name = os.path.basename(safe_path) or 'folder'
    return send_file(memory_file, mimetype='application/zip',
                     as_attachment=True, download_name=f'{folder_name}.zip')


@app.route('/delete/<path:filename>', methods=['POST'])
def delete(filename):
    safe_path = get_safe_path(filename)
    if safe_path is None:
        flash('Invalid path', 'error')
        return redirect(url_for('index'))

    try:
        if os.path.isfile(safe_path):
            os.remove(safe_path)
            flash(f'Deleted: {os.path.basename(safe_path)}', 'success')
        elif os.path.isdir(safe_path):
            shutil.rmtree(safe_path)
            flash(f'Deleted folder: {os.path.basename(safe_path)}', 'success')
        else:
            flash('File or directory not found', 'error')
    except OSError as e:
        flash(f'Error deleting: {str(e)}', 'error')

    parent = os.path.dirname(filename) if filename else ''
    return redirect(url_for('index', subpath=parent) if parent else url_for('index'))


@app.route('/rename/<path:filename>', methods=['GET', 'POST'])
def rename(filename):
    safe_path = get_safe_path(filename)
    if safe_path is None:
        flash('Invalid path', 'error')
        return redirect(url_for('index'))
    if not os.path.exists(safe_path):
        flash('File or directory not found', 'error')
        return redirect(url_for('index'))

    current_name = os.path.basename(safe_path)
    parent_dir = os.path.dirname(safe_path)
    parent_rel = get_relative_path(parent_dir)

    if request.method == 'POST':
        new_name = request.form.get('new_name', '').strip()
        if not new_name:
            flash('New name is required', 'error')
            return redirect(request.url)

        new_path = os.path.join(parent_dir, new_name)
        new_rel = get_relative_path(new_path)

        if not new_rel.startswith(get_relative_path(parent_dir)) and new_rel != '':
            flash('Invalid new name', 'error')
            return redirect(request.url)

        try:
            os.rename(safe_path, new_path)
            flash(f'Renamed to {new_name}', 'success')
            return redirect(url_for('index', subpath=parent_rel))
        except OSError as e:
            flash(f'Error renaming: {str(e)}', 'error')
            return redirect(request.url)

    return render_template('rename.html', filename=filename,
                           current_name=current_name, parent_path=parent_rel)


@app.route('/edit/<path:filename>', methods=['GET', 'POST'])
def edit(filename):
    safe_path = get_safe_path(filename)
    if safe_path is None or not os.path.isfile(safe_path):
        flash('File not found', 'error')
        return redirect(url_for('index'))

    try:
        with open(safe_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception as e:
        flash(f'Error reading file: {str(e)}', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        new_content = request.form.get('content', '')
        try:
            with open(safe_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            flash('File saved successfully', 'success')
            parent = os.path.dirname(filename) if os.path.dirname(filename) else ''
            return redirect(url_for('index', subpath=parent))
        except Exception as e:
            flash(f'Error saving file: {str(e)}', 'error')

    return render_template('edit.html', filename=filename, content=content)


@app.route('/new_folder', methods=['POST'])
def new_folder():
    folder_name = request.form.get('folder_name', '').strip()
    target_path = request.form.get('target_path', '')

    if not folder_name:
        flash('Folder name is required', 'error')
        return redirect(request.referrer or url_for('index'))

    safe_path = get_safe_path(target_path)
    if safe_path is None or not os.path.isdir(safe_path):
        flash('Invalid target directory', 'error')
        return redirect(request.referrer or url_for('index'))

    new_path = os.path.join(safe_path, folder_name)
    try:
        os.mkdir(new_path)
        flash(f'Folder "{folder_name}" created', 'success')
    except FileExistsError:
        flash('Folder already exists', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('index', subpath=target_path) if target_path else url_for('index'))


if __name__ == '__main__':
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
    except OSError:
        ip = '127.0.0.1'

    print(f'Online File Manager running at:')
    print(f'  Local:   http://127.0.0.1:5000')
    print(f'  Network: http://{ip}:5000')
    print(f'  Home:    {HOME_DIR}')
    print(f'  Root:    {BASE_DIR}')
    app.run(host='0.0.0.0', port=5000, debug=True)
