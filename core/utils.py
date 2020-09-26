def truncate(text, max_length=64):
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + '...'
