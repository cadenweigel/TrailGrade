import os


def get_project_root():
    """Returns the absolute path to the project root directory"""
    # get directory of this file (utils/__init__.py)
    curr = os.path.dirname(os.path.abspath(__file__))
    # go up one level to root
    return os.path.dirname(curr)


def get_db_path():
    """Returns the absolute path to the database file"""
    return os.path.join(get_project_root(), "data", "trails.db")


def get_trail_files():
    """Returns the absolute path to the trail files directory"""
    return os.path.join(get_project_root(), "storage", "trail_files")


def get_trail_file_name(full_path):
    """Extracts just the trail file name from a full path"""
    return os.path.basename(full_path)


def get_full_trail_path(file_name):
    """Returns the absolute path to a trail file based on the file name"""
    if os.path.isabs(file_name):
        return file_name
    return os.path.join(get_trail_files(), file_name)
