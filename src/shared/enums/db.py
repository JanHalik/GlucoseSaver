from enum import Enum
class PollerState(str,Enum):
    ACTIVE="active"
    INACTIVE="inactive"
    ERROR="error"