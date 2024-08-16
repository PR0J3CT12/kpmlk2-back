def validate_work_type_for_class(type_, class_):
    class_ = int(class_)
    type_ = int(type_)
    if class_ == 4:
        if type_ not in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
            return False
    if class_ in [5, 6, 7]:
        if type_ not in [0, 1, 9, 10, 11]:
            return False
    return True


def validate_work_type_for_group_type(work_type, group_type):
    work_type = int(work_type)
    if group_type is not None:
        group_type = int(group_type)
        if group_type == 0:
            if work_type not in [0, 1, 9, 10]:
                return False
        if group_type in [1, 2, 3]:
            if work_type not in [0, 1, 9, 11]:
                return False
    else:
        if work_type not in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
            return False
    return True