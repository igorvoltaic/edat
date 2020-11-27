def trim_filename(name: str) -> str:
    """ Trim filename to be no longer than 150 characters """
    name = name[:-4]  # getting rid of .csv extension
    trimmed_name = (f"{name[:146]}.csv")  # cut file to be 150 characters
    return trimmed_name
