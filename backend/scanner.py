import os

def format_size(size_in_bytes):
    """Translates raw bytes into human-readable numbers (MB, GB, etc.)."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0

def get_directory_size(path):
    """Recursively digs into folders to find their total size."""
    total_size = 0
    try:
        # os.scandir is lightning fast because it grabs file sizes immediately
        for entry in os.scandir(path):
            try:
                if entry.is_file(follow_symlinks=False):
                    total_size += entry.stat(follow_symlinks=False).st_size
                elif entry.is_dir(follow_symlinks=False):
                    total_size += get_directory_size(entry.path)
            except (PermissionError, FileNotFoundError):
                # Ignore hidden system files we aren't allowed to touch
                continue
    except (PermissionError, FileNotFoundError):
        pass
    
    return total_size

def analyze_path(target_path):
    """Scans the immediate contents of a folder and ranks them."""
    results = []
    
    try:
        for entry in os.scandir(target_path):
            try:
                item_size = 0
                is_dir = entry.is_dir(follow_symlinks=False)
                
                if is_dir:
                    item_size = get_directory_size(entry.path)
                else:
                    item_size = entry.stat(follow_symlinks=False).st_size
                
                # Package the data so our UI can read it easily
                results.append({
                    "name": entry.name,
                    "path": entry.path, # We save the path for our future right-click menu!
                    "size_bytes": item_size,
                    "type": "Folder" if is_dir else "File"
                })
            except (PermissionError, FileNotFoundError):
                continue
    except Exception as e:
        print(f"Error: {e}")

    # Sort from largest to smallest
    results.sort(key=lambda x: x["size_bytes"], reverse=True)
    return results