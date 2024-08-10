def message_data_list_to_str(message_list: list[str], show_timestamp=True) -> str:
    """
    Convert a message data list to a single string, with optional timestamp
    """
    time, user, message = message_list
    if show_timestamp:
        return f"\n{time} | {user}: {message}"
    else:
        return f"{user}: {message}"
