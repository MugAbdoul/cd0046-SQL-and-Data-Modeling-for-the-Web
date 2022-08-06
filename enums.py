import enum


class Genre(enum.Enum):
    Alternative = 'Alternative'
    Blues = 'Blues'
    # add all fields
    ...

    @classmethod
    def choices(cls):
        """ Methods decorated with @classmethod can be called statically without having an instance of the class."""
        return [(choice.name, choice.value) for choice in cls]


class State(enum.Enum):
    AL = 'AL'
    AK = 'AK'
    # add all fields
    ...

    @classmethod
    def choices(cls):
        return [(choice.name, choice.value) for choice in cls]