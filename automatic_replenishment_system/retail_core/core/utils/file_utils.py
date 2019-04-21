import os


class OSFileOperations:
    @staticmethod
    def ensure_directory(file_path):
        directory = OSFileOperations.get_dir_path(file_path)
        if not directory:
            # file_path is a file, no need to create directory.
            return
        if not OSFileOperations.entity_exists(directory):
            os.makedirs(directory)

    @staticmethod
    def entity_exists(file_path):
        return os.path.exists(file_path)

    @staticmethod
    def get_dir_path(file_path):
        directory = os.path.dirname(file_path)
        return directory
