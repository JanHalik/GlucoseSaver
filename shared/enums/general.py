from enum import Enum
class SortOrder(str,Enum):
    ASC="asc"
    DESC="desc"
class WSOperation(str,Enum):
    CHANGE="change"
    ADD="add"
    DELETE="delete"
class EntityName(str,Enum):
    GLUCOSE="glucose"
    PATIENT="patient"