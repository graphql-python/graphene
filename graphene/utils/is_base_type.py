
def is_base_type(bases, _type):
    return any(b for b in bases if isinstance(b, _type))
