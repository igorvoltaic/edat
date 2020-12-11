""" Custom Exception classes used throughout the application
"""


class FileAccessError(Exception):
    """ Exceptions called in case there was any file access problem """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
