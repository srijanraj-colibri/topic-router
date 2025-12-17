def parse_alfresco_event(body: str) -> dict:
    """
    Converts Alfresco Java Map string:
    {key=value, key2=value2}
    into Python dict.
    """
    body = body.strip()

    if not (body.startswith("{") and body.endswith("}")):
        raise ValueError("Invalid Alfresco event format")

    content = body[1:-1].strip()
    if not content:
        return {}

    data = {}
    for part in content.split(","):
        key, value = part.split("=", 1)
        data[key.strip()] = value.strip()

    return data
