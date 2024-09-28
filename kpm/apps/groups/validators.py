def validate_group_type_for_class(type_, class_):
    class_ = int(class_)
    if class_ == 4:
        return True
    type_ = int(type_)
    if class_ in [5, 6]:
        if type_ not in [0, 1]:
            return False
    if class_ == 7:
        if type_ not in [0, 2, 3]:
            return False
    if class_ in [8, 9]:
        if type_ not in [4, 5, 6]:
            return False
    return True