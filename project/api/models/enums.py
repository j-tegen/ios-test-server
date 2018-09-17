import enum


class EnumBase(enum.Enum):
    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)

#TBI