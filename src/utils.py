import os

def count_items(path):
    """Count the total number of directories and files in a given path."""
    total = 0
    try:
        for _, dirs, files in os.walk(path):
            total += len(dirs) + len(files)
    except Exception as e:
        print(f"Error counting items: {e}")
    return total

def filter_items(items, path, ignore_temp_files):
    """Filter directories and files based on whether temporary files should be ignored."""
    folders = sorted([item for item in items if os.path.isdir(os.path.join(path, item))])
    files = sorted([item for item in items if os.path.isfile(os.path.join(path, item))])

    if ignore_temp_files:
        folders = [f for f in folders if f not in [
            '.git', '.svn', '.hg', 'node_modules', 'venv', 'dist', 'build', 
            'target', '.idea', '.vscode', '.Trash', '.cache', '__pycache__', 
            'coverage'
        ]]
        files = [f for f in files if not (
            f.startswith('.') or f.endswith('.log') or f.endswith('~') or 
            f.endswith('.pyc') or f.endswith('.tmp') or f.endswith('.temp') or 
            f in ['Thumbs.db', '.DS_Store', '.env', '.coverage']
        )]
    return folders, files