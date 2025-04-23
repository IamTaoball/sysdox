def sendLog(message: str, level: int = 0) -> str:
    """
    Send a log message for no reason
    """
    if level == 0:
        log_message = message
    elif level == 1:
        log_message = f"INFO: {message}"
    elif level == 2:
        log_message = f"WARNING: {message}"
    elif level == 3:
        log_message = f"ERROR: {message}"
    else:
        log_message = f"UNKNOWN LEVEL ({level}): {message}"
    
    print(log_message)
    return log_message