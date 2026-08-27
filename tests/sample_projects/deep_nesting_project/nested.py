def deeply_nested(values):
    for value in values:
        if value:
            while value > 0:
                try:
                    if value % 2:
                        return value
                finally:
                    value -= 1
    return None

