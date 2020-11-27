def recreate_filename(tmpfilename: str) -> str:
    orig_filename = tmpfilename.split('__tmpfile__')[0]
    return orig_filename
