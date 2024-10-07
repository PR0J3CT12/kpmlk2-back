def validate_class(class_):
    if class_ not in [4, 5, 6, 8, 9, '4', '5', '6', '7', '8', '9']:
        return False
    return True


def validate_work_type_for_class(type_, class_):
    class_ = int(class_)
    type_ = int(type_)
    if class_ == 4:
        if type_ not in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
            return False
    if class_ in [5, 6, 7]:
        if type_ not in [0, 1, 9, 10, 11]:
            return False
    if class_ in [8, 9]:
        if type_ not in [0, 1, 11]:
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
        if group_type in [4, 5, 6]:
            if work_type not in [0, 1, 9, 11]:
                return False
    else:
        if work_type not in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
            return False
    return True


def validate_work_class_for_work_course(work_class, work_course):
    try:
        work_class = int(work_class)
        work_course = int(work_course)
        if work_class == 4:
            if work_course == 0:
                return True
        elif work_class in [5, 6]:
            if work_course in [1, 2]:
                return True
        elif work_class == 7:
            if work_course in [1, 3, 4]:
                return True
        elif work_class in [8, 9]:
            if work_course in [5, 6, 7]:
                return True
        return False
    except Exception:
        return False


def validate_work_course_for_group_type(work_course, group_type):
    try:
        work_course = int(work_course)
        if group_type is None:
            if work_course == 0:
                return True
        else:
            group_type = int(group_type)
            if group_type == 0:
                if work_course == 1:
                    return True
            if group_type == 1:
                if work_course == 2:
                    return True
            if group_type == 2:
                if work_course == 3:
                    return True
            if group_type == 3:
                if work_course == 4:
                    return True
            if group_type in [4, 5, 6]:
                if work_course in [5, 6, 7]:
                    return True
        return False
    except Exception:
        return False
