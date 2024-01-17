def get_name_from_path(in_path: str, with_suffix: bool = True):
    """Return the name + number of prediction from input path"""
    name_split = in_path.split("_")
    method = name_split[0]
    if (
        len(name_split) == 5 and with_suffix
    ):  # Means there are multiple outputs from this model
        if "rp14" in in_path:
            if len(name_split) > 5:
                method = method + "_" + name_split[3]
        else:
            method = method + "_" + name_split[2]
    return method
