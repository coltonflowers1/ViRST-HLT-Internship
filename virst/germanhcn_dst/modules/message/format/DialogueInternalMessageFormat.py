# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = message_type_from_dict(json.loads(json_string))
#     result = error_data_from_dict(json.loads(json_string))
#     result = i_error_data_from_dict(json.loads(json_string))
#     result = error_type_from_dict(json.loads(json_string))
#     result = general_message_from_dict(json.loads(json_string))
#     result = i_general_message_from_dict(json.loads(json_string))
#     result = request_message_from_dict(json.loads(json_string))
#     result = i_request_message_from_dict(json.loads(json_string))
#     result = user_input_message_from_dict(json.loads(json_string))
#     result = i_user_input_message_from_dict(json.loads(json_string))
#     result = system_output_message_from_dict(json.loads(json_string))
#     result = i_system_output_message_from_dict(json.loads(json_string))
#     result = system_output_data_from_dict(json.loads(json_string))
#     result = i_system_output_data_from_dict(json.loads(json_string))
#     result = system_dialogue_message_from_dict(json.loads(json_string))
#     result = i_system_dialogue_message_from_dict(json.loads(json_string))
#     result = system_dialogue_data_from_dict(json.loads(json_string))
#     result = i_system_dialogue_data_from_dict(json.loads(json_string))
#     result = system_dialogue_operation_from_dict(json.loads(json_string))
#     result = error_message_from_dict(json.loads(json_string))
#     result = i_error_message_from_dict(json.loads(json_string))

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Any, List, TypeVar, Type, cast, Callable


T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    assert isinstance(x, c)
    return x.value


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


class ErrorType(Enum):
    """the type of error
    
    type of errors
    """
    FORMAT = "format"
    UNKNOWN_TYPE = "unknown_type"
    UNKONWN = "unkonwn"
    UNSUPPORTED_TYPE = "unsupported_type"


@dataclass
class IErrorData:
    """Error details"""
    """the type of error"""
    error: Optional[ErrorType]
    """the error message / description"""
    message: Optional[str]

    @staticmethod
    def from_dict(obj: Any) -> 'IErrorData':
        assert isinstance(obj, dict)
        error = from_union([ErrorType, from_none], obj.get("error"))
        message = from_union([from_str, from_none], obj.get("message"))
        return IErrorData(error, message)

    def to_dict(self) -> dict:
        result: dict = {}
        result["error"] = from_union([lambda x: to_enum(ErrorType, x), from_none], self.error)
        result["message"] = from_union([from_str, from_none], self.message)
        return result


class MessageType(Enum):
    """type of messages for communication between components: the type-field of messages would
    contain the string representation
    
    the message type:
    the sent message contains a string representation of the type
    
    type is "input"
    
    type is "output"
    
    type is "dialogue"
    
    type is "error"
    """
    DIALOGUE = "dialogue"
    ERROR = "error"
    EXERCISE = "exercise"
    HEARTRATE = "heartrate"
    INPUT = "input"
    OUTPUT = "output"
    SESSION = "session"
    SPEECHIO = "speechio"
    STRESS = "stress"
    TOGGLESPEECH = "togglespeech"


@dataclass
class GeneralMessage:
    """Base class for messages"""
    """the data field:
    inheriting classes will have a more specific field-type
    """
    data: Any
    """the timestamp (including milliseconds) for the message"""
    timestamp: Optional[int]
    """the message type:
    the sent message contains a string representation of the type
    """
    type: Optional[MessageType]

    @staticmethod
    def from_dict(obj: Any) -> 'GeneralMessage':
        assert isinstance(obj, dict)
        data = obj.get("data")
        timestamp = from_union([from_int, from_none], obj.get("timestamp"))
        type = from_union([MessageType, from_none], obj.get("type"))
        return GeneralMessage(data, timestamp, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = self.data
        result["timestamp"] = from_union([from_int, from_none], self.timestamp)
        result["type"] = from_union([lambda x: to_enum(MessageType, x), from_none], self.type)
        return result


@dataclass
class IGeneralMessage:
    """Base class for messages"""
    """the data field:
    inheriting classes will have a more specific field-type
    """
    data: Any
    """the timestamp (including milliseconds) for the message"""
    timestamp: Optional[int]
    """the message type:
    the sent message contains a string representation of the type
    """
    type: Optional[MessageType]

    @staticmethod
    def from_dict(obj: Any) -> 'IGeneralMessage':
        assert isinstance(obj, dict)
        data = obj.get("data")
        timestamp = from_union([from_int, from_none], obj.get("timestamp"))
        type = from_union([MessageType, from_none], obj.get("type"))
        return IGeneralMessage(data, timestamp, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = self.data
        result["timestamp"] = from_union([from_int, from_none], self.timestamp)
        result["type"] = from_union([lambda x: to_enum(MessageType, x), from_none], self.type)
        return result


@dataclass
class RequestMessage:
    """Class for request messages: many requests may be indicated by the type property on
    itself; in this case, the timestamp and data properties can be omitted/set to NULL. If
    the data-property is not NULL, the corresponding JSON-string of the "stringified"
    RequestMessage can also be parsed by the class/type indicated by its type property (e.g.
    MessageType.error -&gt; ErrorMessage) In this case, the timestamp property MUST also be
    set, i.e. if data property is set, the message must be "parseable" as GeneralMessage!
    Simple Example: {"type":"stress"} Example with data:
    {"type":"dialogue","timestamp":1562608409039,"data":{"operation":"list"}}
    """
    """the data field:
    may be omitted, but if set, it must adhere to the data type
    as indicated by the type property, AND the timestamp property
    must also be set (if data is set / not NULL).
    """
    data: Any
    """the timestamp (including milliseconds) for the request message:
    if property data is set, the timestamp MUST also be set.
    """
    timestamp: Optional[int]
    """the message type:
    the sent message contains a string representation of the type
    """
    type: Optional[MessageType]

    @staticmethod
    def from_dict(obj: Any) -> 'RequestMessage':
        assert isinstance(obj, dict)
        data = obj.get("data")
        timestamp = from_union([from_int, from_none], obj.get("timestamp"))
        type = from_union([MessageType, from_none], obj.get("type"))
        return RequestMessage(data, timestamp, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = self.data
        result["timestamp"] = from_union([from_int, from_none], self.timestamp)
        result["type"] = from_union([lambda x: to_enum(MessageType, x), from_none], self.type)
        return result


@dataclass
class IRequestMessage:
    """Class for request messages: many requests may be indicated by the type property on
    itself; in this case, the timestamp and data properties can be omitted/set to NULL. If
    the data-property is not NULL, the corresponding JSON-string of the "stringified"
    RequestMessage can also be parsed by the class/type indicated by its type property (e.g.
    MessageType.error -&gt; ErrorMessage) In this case, the timestamp property MUST also be
    set, i.e. if data property is set, the message must be "parseable" as GeneralMessage!
    Simple Example: {"type":"stress"} Example with data:
    {"type":"dialogue","timestamp":1562608409039,"data":{"operation":"list"}}
    """
    """the data field:
    may be omitted, but if set, it must adhere to the data type
    as indicated by the type property, AND the timestamp property
    must also be set (if data is set / not NULL).
    """
    data: Any
    """the timestamp (including milliseconds) for the request message:
    if property data is set, the timestamp MUST also be set.
    """
    timestamp: Optional[int]
    """the message type:
    the sent message contains a string representation of the type
    """
    type: Optional[MessageType]

    @staticmethod
    def from_dict(obj: Any) -> 'IRequestMessage':
        assert isinstance(obj, dict)
        data = obj.get("data")
        timestamp = from_union([from_int, from_none], obj.get("timestamp"))
        type = from_union([MessageType, from_none], obj.get("type"))
        return IRequestMessage(data, timestamp, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = self.data
        result["timestamp"] = from_union([from_int, from_none], self.timestamp)
        result["type"] = from_union([lambda x: to_enum(MessageType, x), from_none], self.type)
        return result


@dataclass
class UserInputMessage:
    """Message for signaling user input: e.g. a user utterance entered via console/terminal, or
    via speech recognition
    """
    """the (natural language) user input as text"""
    data: Optional[str]
    """the timestamp (including milliseconds) for the message"""
    timestamp: Optional[int]
    """type is "input" """
    type: Optional[MessageType]

    @staticmethod
    def from_dict(obj: Any) -> 'UserInputMessage':
        assert isinstance(obj, dict)
        data = from_union([from_str, from_none], obj.get("data"))
        timestamp = from_union([from_int, from_none], obj.get("timestamp"))
        type = from_union([MessageType, from_none], obj.get("type"))
        return UserInputMessage(data, timestamp, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = from_union([from_str, from_none], self.data)
        result["timestamp"] = from_union([from_int, from_none], self.timestamp)
        result["type"] = from_union([lambda x: to_enum(MessageType, x), from_none], self.type)
        return result


@dataclass
class IUserInputMessage:
    """Message for signaling user input: e.g. a user utterance entered via console/terminal, or
    via speech recognition
    """
    """the (natural language) user input as text"""
    data: Optional[str]
    """the timestamp (including milliseconds) for the message"""
    timestamp: Optional[int]
    """type is "input" """
    type: Optional[MessageType]

    @staticmethod
    def from_dict(obj: Any) -> 'IUserInputMessage':
        assert isinstance(obj, dict)
        data = from_union([from_str, from_none], obj.get("data"))
        timestamp = from_union([from_int, from_none], obj.get("timestamp"))
        type = from_union([MessageType, from_none], obj.get("type"))
        return IUserInputMessage(data, timestamp, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = from_union([from_str, from_none], self.data)
        result["timestamp"] = from_union([from_int, from_none], self.timestamp)
        result["type"] = from_union([lambda x: to_enum(MessageType, x), from_none], self.type)
        return result


@dataclass
class SystemOutputData:
    """the system output / prompt
    
    system output/prompt data: e.g. for displaying the system message, showing as toast, or
    as speech synthesis.
    """
    """the dialogue act which corresponds to the system message"""
    dialogue_act: Optional[str]
    """the dialogue state of the system"""
    state: Optional[str]
    """the system message text"""
    text: Optional[str]
    """the type of (user) utterance for which the
    system message refers to
    """
    utterance_type: Optional[str]

    @staticmethod
    def from_dict(obj: Any) -> 'SystemOutputData':
        assert isinstance(obj, dict)
        dialogue_act = from_union([from_str, from_none], obj.get("dialogueAct"))
        state = from_union([from_str, from_none], obj.get("state"))
        text = from_union([from_str, from_none], obj.get("text"))
        utterance_type = from_union([from_str, from_none], obj.get("utteranceType"))
        return SystemOutputData(dialogue_act, state, text, utterance_type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["dialogueAct"] = from_union([from_str, from_none], self.dialogue_act)
        result["state"] = from_union([from_str, from_none], self.state)
        result["text"] = from_union([from_str, from_none], self.text)
        result["utteranceType"] = from_union([from_str, from_none], self.utterance_type)
        return result


@dataclass
class SystemOutputMessage:
    """Message for signaling system output / prompt: e.g. for displaying the system message,
    showing as toast, or as speech synthesis.
    """
    """the system output / prompt"""
    data: Optional[SystemOutputData]
    """the timestamp (including milliseconds) for the message"""
    timestamp: Optional[int]
    """type is "output" """
    type: Optional[MessageType]

    @staticmethod
    def from_dict(obj: Any) -> 'SystemOutputMessage':
        assert isinstance(obj, dict)
        data = from_union([SystemOutputData.from_dict, from_none], obj.get("data"))
        timestamp = from_union([from_int, from_none], obj.get("timestamp"))
        type = from_union([MessageType, from_none], obj.get("type"))
        return SystemOutputMessage(data, timestamp, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = from_union([lambda x: to_class(SystemOutputData, x), from_none], self.data)
        result["timestamp"] = from_union([from_int, from_none], self.timestamp)
        result["type"] = from_union([lambda x: to_enum(MessageType, x), from_none], self.type)
        return result


@dataclass
class ISystemOutputMessage:
    """Message for signaling system output / prompt: e.g. for displaying the system message,
    showing as toast, or as speech synthesis.
    """
    """the system output / prompt"""
    data: Optional[SystemOutputData]
    """the timestamp (including milliseconds) for the message"""
    timestamp: Optional[int]
    """type is "output" """
    type: Optional[MessageType]

    @staticmethod
    def from_dict(obj: Any) -> 'ISystemOutputMessage':
        assert isinstance(obj, dict)
        data = from_union([SystemOutputData.from_dict, from_none], obj.get("data"))
        timestamp = from_union([from_int, from_none], obj.get("timestamp"))
        type = from_union([MessageType, from_none], obj.get("type"))
        return ISystemOutputMessage(data, timestamp, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = from_union([lambda x: to_class(SystemOutputData, x), from_none], self.data)
        result["timestamp"] = from_union([from_int, from_none], self.timestamp)
        result["type"] = from_union([lambda x: to_enum(MessageType, x), from_none], self.type)
        return result


@dataclass
class ISystemOutputData:
    """system output/prompt data: e.g. for displaying the system message, showing as toast, or
    as speech synthesis.
    """
    """the dialogue act which corresponds to the system message"""
    dialogue_act: Optional[str]
    """the dialogue state of the system"""
    state: Optional[str]
    """the system message text"""
    text: Optional[str]
    """the type of (user) utterance for which the
    system message refers to
    """
    utterance_type: Optional[str]

    @staticmethod
    def from_dict(obj: Any) -> 'ISystemOutputData':
        assert isinstance(obj, dict)
        dialogue_act = from_union([from_str, from_none], obj.get("dialogueAct"))
        state = from_union([from_str, from_none], obj.get("state"))
        text = from_union([from_str, from_none], obj.get("text"))
        utterance_type = from_union([from_str, from_none], obj.get("utteranceType"))
        return ISystemOutputData(dialogue_act, state, text, utterance_type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["dialogueAct"] = from_union([from_str, from_none], self.dialogue_act)
        result["state"] = from_union([from_str, from_none], self.state)
        result["text"] = from_union([from_str, from_none], self.text)
        result["utteranceType"] = from_union([from_str, from_none], self.utterance_type)
        return result


class SystemDialogueOperation(Enum):
    """the operation (w.r.t. dialogues/exercises) that is requested by the message
    
    dialogue operations: e.g. query the list of all dialogues/exercises, set/start the system
    with a specific dialogue/exercise
    """
    GET = "get"
    LIST = "list"
    SET = "set"


@dataclass
class SystemDialogueData:
    """the system output / prompt
    
    system dialogue(s) message: e.g. querying list of dialogues/exercises, setting/starting
    an exercise
    """
    """a dialogue/exercises
    
    may be NULL
    """
    dialogue: Optional[str]
    """list of dialogues/exercises
    
    may be NULL
    """
    dialogues: Optional[List[str]]
    """the operation (w.r.t. dialogues/exercises) that is requested by the message"""
    operation: Optional[SystemDialogueOperation]

    @staticmethod
    def from_dict(obj: Any) -> 'SystemDialogueData':
        assert isinstance(obj, dict)
        dialogue = from_union([from_str, from_none], obj.get("dialogue"))
        dialogues = from_union([lambda x: from_list(from_str, x), from_none], obj.get("dialogues"))
        operation = from_union([SystemDialogueOperation, from_none], obj.get("operation"))
        return SystemDialogueData(dialogue, dialogues, operation)

    def to_dict(self) -> dict:
        result: dict = {}
        result["dialogue"] = from_union([from_str, from_none], self.dialogue)
        result["dialogues"] = from_union([lambda x: from_list(from_str, x), from_none], self.dialogues)
        result["operation"] = from_union([lambda x: to_enum(SystemDialogueOperation, x), from_none], self.operation)
        return result


@dataclass
class SystemDialogueMessage:
    """Message for signaling system output / prompt: e.g. for displaying the system message,
    showing as toast, or as speech synthesis.
    """
    """the system output / prompt"""
    data: Optional[SystemDialogueData]
    """the timestamp (including milliseconds) for the message"""
    timestamp: Optional[int]
    """type is "dialogue" """
    type: Optional[MessageType]

    @staticmethod
    def from_dict(obj: Any) -> 'SystemDialogueMessage':
        assert isinstance(obj, dict)
        data = from_union([SystemDialogueData.from_dict, from_none], obj.get("data"))
        timestamp = from_union([from_int, from_none], obj.get("timestamp"))
        type = from_union([MessageType, from_none], obj.get("type"))
        return SystemDialogueMessage(data, timestamp, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = from_union([lambda x: to_class(SystemDialogueData, x), from_none], self.data)
        result["timestamp"] = from_union([from_int, from_none], self.timestamp)
        result["type"] = from_union([lambda x: to_enum(MessageType, x), from_none], self.type)
        return result


@dataclass
class ISystemDialogueMessage:
    """Message for signaling system output / prompt: e.g. for displaying the system message,
    showing as toast, or as speech synthesis.
    """
    """the system output / prompt"""
    data: Optional[SystemDialogueData]
    """the timestamp (including milliseconds) for the message"""
    timestamp: Optional[int]
    """type is "dialogue" """
    type: Optional[MessageType]

    @staticmethod
    def from_dict(obj: Any) -> 'ISystemDialogueMessage':
        assert isinstance(obj, dict)
        data = from_union([SystemDialogueData.from_dict, from_none], obj.get("data"))
        timestamp = from_union([from_int, from_none], obj.get("timestamp"))
        type = from_union([MessageType, from_none], obj.get("type"))
        return ISystemDialogueMessage(data, timestamp, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = from_union([lambda x: to_class(SystemDialogueData, x), from_none], self.data)
        result["timestamp"] = from_union([from_int, from_none], self.timestamp)
        result["type"] = from_union([lambda x: to_enum(MessageType, x), from_none], self.type)
        return result


@dataclass
class ISystemDialogueData:
    """system dialogue(s) message: e.g. querying list of dialogues/exercises, setting/starting
    an exercise
    """
    """a dialogue/exercises
    
    may be NULL
    """
    dialogue: Optional[str]
    """list of dialogues/exercises
    
    may be NULL
    """
    dialogues: Optional[List[str]]
    """the operation (w.r.t. dialogues/exercises) that is requested by the message"""
    operation: Optional[SystemDialogueOperation]

    @staticmethod
    def from_dict(obj: Any) -> 'ISystemDialogueData':
        assert isinstance(obj, dict)
        dialogue = from_union([from_str, from_none], obj.get("dialogue"))
        dialogues = from_union([lambda x: from_list(from_str, x), from_none], obj.get("dialogues"))
        operation = from_union([SystemDialogueOperation, from_none], obj.get("operation"))
        return ISystemDialogueData(dialogue, dialogues, operation)

    def to_dict(self) -> dict:
        result: dict = {}
        result["dialogue"] = from_union([from_str, from_none], self.dialogue)
        result["dialogues"] = from_union([lambda x: from_list(from_str, x), from_none], self.dialogues)
        result["operation"] = from_union([lambda x: to_enum(SystemDialogueOperation, x), from_none], self.operation)
        return result


@dataclass
class ErrorData:
    """Error details
    
    the error cause / details
    """
    """the type of error"""
    error: Optional[ErrorType]
    """the error message / description"""
    message: Optional[str]

    @staticmethod
    def from_dict(obj: Any) -> 'ErrorData':
        assert isinstance(obj, dict)
        error = from_union([ErrorType, from_none], obj.get("error"))
        message = from_union([from_str, from_none], obj.get("message"))
        return ErrorData(error, message)

    def to_dict(self) -> dict:
        result: dict = {}
        result["error"] = from_union([lambda x: to_enum(ErrorType, x), from_none], self.error)
        result["message"] = from_union([from_str, from_none], self.message)
        return result


@dataclass
class ErrorMessage:
    """Error message for signaling errornuous requests etc."""
    """the error cause / details"""
    data: Optional[ErrorData]
    """the timestamp (including milliseconds) for the message"""
    timestamp: Optional[int]
    """type is "error" """
    type: Optional[MessageType]

    @staticmethod
    def from_dict(obj: Any) -> 'ErrorMessage':
        assert isinstance(obj, dict)
        data = from_union([ErrorData.from_dict, from_none], obj.get("data"))
        timestamp = from_union([from_int, from_none], obj.get("timestamp"))
        type = from_union([MessageType, from_none], obj.get("type"))
        return ErrorMessage(data, timestamp, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = from_union([lambda x: to_class(ErrorData, x), from_none], self.data)
        result["timestamp"] = from_union([from_int, from_none], self.timestamp)
        result["type"] = from_union([lambda x: to_enum(MessageType, x), from_none], self.type)
        return result


@dataclass
class IErrorMessage:
    """Error message for signaling errornuous requests etc."""
    """the error cause / details"""
    data: Optional[ErrorData]
    """the timestamp (including milliseconds) for the message"""
    timestamp: Optional[int]
    """type is "error" """
    type: Optional[MessageType]

    @staticmethod
    def from_dict(obj: Any) -> 'IErrorMessage':
        assert isinstance(obj, dict)
        data = from_union([ErrorData.from_dict, from_none], obj.get("data"))
        timestamp = from_union([from_int, from_none], obj.get("timestamp"))
        type = from_union([MessageType, from_none], obj.get("type"))
        return IErrorMessage(data, timestamp, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = from_union([lambda x: to_class(ErrorData, x), from_none], self.data)
        result["timestamp"] = from_union([from_int, from_none], self.timestamp)
        result["type"] = from_union([lambda x: to_enum(MessageType, x), from_none], self.type)
        return result


def message_type_from_dict(s: Any) -> MessageType:
    return MessageType(s)


def message_type_to_dict(x: MessageType) -> Any:
    return to_enum(MessageType, x)


def error_data_from_dict(s: Any) -> ErrorData:
    return ErrorData.from_dict(s)


def error_data_to_dict(x: ErrorData) -> Any:
    return to_class(ErrorData, x)


def i_error_data_from_dict(s: Any) -> IErrorData:
    return IErrorData.from_dict(s)


def i_error_data_to_dict(x: IErrorData) -> Any:
    return to_class(IErrorData, x)


def error_type_from_dict(s: Any) -> ErrorType:
    return ErrorType(s)


def error_type_to_dict(x: ErrorType) -> Any:
    return to_enum(ErrorType, x)


def general_message_from_dict(s: Any) -> GeneralMessage:
    return GeneralMessage.from_dict(s)


def general_message_to_dict(x: GeneralMessage) -> Any:
    return to_class(GeneralMessage, x)


def i_general_message_from_dict(s: Any) -> IGeneralMessage:
    return IGeneralMessage.from_dict(s)


def i_general_message_to_dict(x: IGeneralMessage) -> Any:
    return to_class(IGeneralMessage, x)


def request_message_from_dict(s: Any) -> RequestMessage:
    return RequestMessage.from_dict(s)


def request_message_to_dict(x: RequestMessage) -> Any:
    return to_class(RequestMessage, x)


def i_request_message_from_dict(s: Any) -> IRequestMessage:
    return IRequestMessage.from_dict(s)


def i_request_message_to_dict(x: IRequestMessage) -> Any:
    return to_class(IRequestMessage, x)


def user_input_message_from_dict(s: Any) -> UserInputMessage:
    return UserInputMessage.from_dict(s)


def user_input_message_to_dict(x: UserInputMessage) -> Any:
    return to_class(UserInputMessage, x)


def i_user_input_message_from_dict(s: Any) -> IUserInputMessage:
    return IUserInputMessage.from_dict(s)


def i_user_input_message_to_dict(x: IUserInputMessage) -> Any:
    return to_class(IUserInputMessage, x)


def system_output_message_from_dict(s: Any) -> SystemOutputMessage:
    return SystemOutputMessage.from_dict(s)


def system_output_message_to_dict(x: SystemOutputMessage) -> Any:
    return to_class(SystemOutputMessage, x)


def i_system_output_message_from_dict(s: Any) -> ISystemOutputMessage:
    return ISystemOutputMessage.from_dict(s)


def i_system_output_message_to_dict(x: ISystemOutputMessage) -> Any:
    return to_class(ISystemOutputMessage, x)


def system_output_data_from_dict(s: Any) -> SystemOutputData:
    return SystemOutputData.from_dict(s)


def system_output_data_to_dict(x: SystemOutputData) -> Any:
    return to_class(SystemOutputData, x)


def i_system_output_data_from_dict(s: Any) -> ISystemOutputData:
    return ISystemOutputData.from_dict(s)


def i_system_output_data_to_dict(x: ISystemOutputData) -> Any:
    return to_class(ISystemOutputData, x)


def system_dialogue_message_from_dict(s: Any) -> SystemDialogueMessage:
    return SystemDialogueMessage.from_dict(s)


def system_dialogue_message_to_dict(x: SystemDialogueMessage) -> Any:
    return to_class(SystemDialogueMessage, x)


def i_system_dialogue_message_from_dict(s: Any) -> ISystemDialogueMessage:
    return ISystemDialogueMessage.from_dict(s)


def i_system_dialogue_message_to_dict(x: ISystemDialogueMessage) -> Any:
    return to_class(ISystemDialogueMessage, x)


def system_dialogue_data_from_dict(s: Any) -> SystemDialogueData:
    return SystemDialogueData.from_dict(s)


def system_dialogue_data_to_dict(x: SystemDialogueData) -> Any:
    return to_class(SystemDialogueData, x)


def i_system_dialogue_data_from_dict(s: Any) -> ISystemDialogueData:
    return ISystemDialogueData.from_dict(s)


def i_system_dialogue_data_to_dict(x: ISystemDialogueData) -> Any:
    return to_class(ISystemDialogueData, x)


def system_dialogue_operation_from_dict(s: Any) -> SystemDialogueOperation:
    return SystemDialogueOperation(s)


def system_dialogue_operation_to_dict(x: SystemDialogueOperation) -> Any:
    return to_enum(SystemDialogueOperation, x)


def error_message_from_dict(s: Any) -> ErrorMessage:
    return ErrorMessage.from_dict(s)


def error_message_to_dict(x: ErrorMessage) -> Any:
    return to_class(ErrorMessage, x)


def i_error_message_from_dict(s: Any) -> IErrorMessage:
    return IErrorMessage.from_dict(s)


def i_error_message_to_dict(x: IErrorMessage) -> Any:
    return to_class(IErrorMessage, x)
