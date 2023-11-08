# pylint: skip-file
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class event_type_enum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    DEPOSIT: _ClassVar[event_type_enum]
    WITHDRAW: _ClassVar[event_type_enum]
    QUERY: _ClassVar[event_type_enum]
DEPOSIT: event_type_enum
WITHDRAW: event_type_enum
QUERY: event_type_enum

class branchEventRequest(_message.Message):
    __slots__ = ["event_id", "customer_id", "event_type", "money", "logical_clock", "customer_request_id"]
    EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    MONEY_FIELD_NUMBER: _ClassVar[int]
    LOGICAL_CLOCK_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    event_id: int
    customer_id: int
    event_type: event_type_enum
    money: float
    logical_clock: int
    customer_request_id: int
    def __init__(self, event_id: _Optional[int] = ..., customer_id: _Optional[int] = ..., event_type: _Optional[_Union[event_type_enum, str]] = ..., money: _Optional[float] = ..., logical_clock: _Optional[int] = ..., customer_request_id: _Optional[int] = ...) -> None: ...

class branchEventResponse(_message.Message):
    __slots__ = ["event_id", "event_type", "money", "balance", "is_success", "logical_clock"]
    EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    MONEY_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    IS_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    LOGICAL_CLOCK_FIELD_NUMBER: _ClassVar[int]
    event_id: int
    event_type: event_type_enum
    money: float
    balance: float
    is_success: bool
    logical_clock: int
    def __init__(self, event_id: _Optional[int] = ..., event_type: _Optional[_Union[event_type_enum, str]] = ..., money: _Optional[float] = ..., balance: _Optional[float] = ..., is_success: bool = ..., logical_clock: _Optional[int] = ...) -> None: ...
