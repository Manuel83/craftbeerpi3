import os


def get_base_path():
    marker_file = "run.py"

    current_path =  os.getcwd()

    while current_path != 0:
        if marker_file in os.listdir(current_path):
            return current_path

        current_path = os.path.dirname(os.path.normpath(current_path))
