class IOEngineMeta(type):
    def __new__(mcs, name, bases, class_dict: dict):
        cls = type.__new__(mcs, name, bases, class_dict)
        return cls

    def __init__(cls, name, bases, class_dict):
        super(IOEngineMeta, cls).__init__()


class IOEngine(metaclass=IOEngineMeta):
    """run I/O-driven applications"""
    pass

