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
#     result = hr_message_from_dict(json.loads(json_string))
#     result = i_hr_message_from_dict(json.loads(json_string))
#     result = stress_message_from_dict(json.loads(json_string))
#     result = i_stress_message_from_dict(json.loads(json_string))
#     result = stress_prediction_from_dict(json.loads(json_string))
#     result = i_stress_prediction_from_dict(json.loads(json_string))
#     result = speech_message_from_dict(json.loads(json_string))
#     result = i_speech_message_from_dict(json.loads(json_string))
#     result = toggle_speech_message_from_dict(json.loads(json_string))
#     result = i_toggle_speech_message_from_dict(json.loads(json_string))
#     result = session_message_from_dict(json.loads(json_string))
#     result = i_session_message_from_dict(json.loads(json_string))
#     result = exercise_data_from_dict(json.loads(json_string))
#     result = i_exercise_data_from_dict(json.loads(json_string))
#     result = exercise_state_from_dict(json.loads(json_string))
#     result = exercise_message_from_dict(json.loads(json_string))
#     result = i_exercise_message_from_dict(json.loads(json_string))
#     result = error_message_from_dict(json.loads(json_string))
#     result = i_error_message_from_dict(json.loads(json_string))

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Any, TypeVar, Type, cast


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


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def to_float(x: Any) -> float:
    assert isinstance(x, float)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


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
    
    type is "heartrate"
    
    type is "stress"
    
    type is "speechio"
    
    type is "togglespeech"
    
    type is "session"
    
    type is "exercise"
    
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
class HrMessage:
    """Message for signaling (changed) heart rate"""
    """the heart rate: a positive integer"""
    data: Optional[int]
    """the timestamp (including milliseconds) for the message"""
    timestamp: Optional[int]
    """type is "heartrate" """
    type: Optional[MessageType]

    @staticmethod
    def from_dict(obj: Any) -> 'HrMessage':
        assert isinstance(obj, dict)
        data = from_union([from_int, from_none], obj.get("data"))
        timestamp = from_union([from_int, from_none], obj.get("timestamp"))
        type = from_union([MessageType, from_none], obj.get("type"))
        return HrMessage(data, timestamp, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = from_union([from_int, from_none], self.data)
        result["timestamp"] = from_union([from_int, from_none], self.timestamp)
        result["type"] = from_union([lambda x: to_enum(MessageType, x), from_none], self.type)
        return result


@dataclass
class IHrMessage:
    """Message for signaling (changed) heart rate"""
    """the heart rate: a positive integer"""
    data: Optional[int]
    """the timestamp (including milliseconds) for the message"""
    timestamp: Optional[int]
    """type is "heartrate" """
    type: Optional[MessageType]

    @staticmethod
    def from_dict(obj: Any) -> 'IHrMessage':
        assert isinstance(obj, dict)
        data = from_union([from_int, from_none], obj.get("data"))
        timestamp = from_union([from_int, from_none], obj.get("timestamp"))
        type = from_union([MessageType, from_none], obj.get("type"))
        return IHrMessage(data, timestamp, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = from_union([from_int, from_none], self.data)
        result["timestamp"] = from_union([from_int, from_none], self.timestamp)
        result["type"] = from_union([lambda x: to_enum(MessageType, x), from_none], self.type)
        return result


@dataclass
class StressPrediction:
    """the stress level / classification
    
    prediction for stress levels / classification
    """
    """prediction for no-stress/relaxed level:
    floating point value between [0, 1]
    """
    no_stress: Optional[float]
    """prediction for the stress level:
    floating point value between [0, 1]
    """
    stress: Optional[float]

    @staticmethod
    def from_dict(obj: Any) -> 'StressPrediction':
        assert isinstance(obj, dict)
        no_stress = from_union([from_float, from_none], obj.get("noStress"))
        stress = from_union([from_float, from_none], obj.get("stress"))
        return StressPrediction(no_stress, stress)

    def to_dict(self) -> dict:
        result: dict = {}
        result["noStress"] = from_union([to_float, from_none], self.no_stress)
        result["stress"] = from_union([to_float, from_none], self.stress)
        return result


@dataclass
class StressMessage:
    """Message for signaling (changed) stress level"""
    """the stress level / classification"""
    data: Optional[StressPrediction]
    """the timestamp (including milliseconds) for the message"""
    timestamp: Optional[int]
    """type is "stress" """
    type: Optional[MessageType]

    @staticmethod
    def from_dict(obj: Any) -> 'StressMessage':
        assert isinstance(obj, dict)
        data = from_union([StressPrediction.from_dict, from_none], obj.get("data"))
        timestamp = from_union([from_int, from_none], obj.get("timestamp"))
        type = from_union([MessageType, from_none], obj.get("type"))
        return StressMessage(data, timestamp, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = from_union([lambda x: to_class(StressPrediction, x), from_none], self.data)
        result["timestamp"] = from_union([from_int, from_none], self.timestamp)
        result["type"] = from_union([lambda x: to_enum(MessageType, x), from_none], self.type)
        return result


@dataclass
class IStressMessage:
    """Message for signaling (changed) stress level"""
    """the stress level / classification"""
    data: Optional[StressPrediction]
    """the timestamp (including milliseconds) for the message"""
    timestamp: Optional[int]
    """type is "stress" """
    type: Optional[MessageType]

    @staticmethod
    def from_dict(obj: Any) -> 'IStressMessage':
        assert isinstance(obj, dict)
        data = from_union([StressPrediction.from_dict, from_none], obj.get("data"))
        timestamp = from_union([from_int, from_none], obj.get("timestamp"))
        type = from_union([MessageType, from_none], obj.get("type"))
        return IStressMessage(data, timestamp, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = from_union([lambda x: to_class(StressPrediction, x), from_none], self.data)
        result["timestamp"] = from_union([from_int, from_none], self.timestamp)
        result["type"] = from_union([lambda x: to_enum(MessageType, x), from_none], self.type)
        return result


@dataclass
class IStressPrediction:
    """prediction for stress levels / classification"""
    """prediction for no-stress/relaxed level:
    floating point value between [0, 1]
    """
    no_stress: Optional[float]
    """prediction for the stress level:
    floating point value between [0, 1]
    """
    stress: Optional[float]

    @staticmethod
    def from_dict(obj: Any) -> 'IStressPrediction':
        assert isinstance(obj, dict)
        no_stress = from_union([from_float, from_none], obj.get("noStress"))
        stress = from_union([from_float, from_none], obj.get("stress"))
        return IStressPrediction(no_stress, stress)

    def to_dict(self) -> dict:
        result: dict = {}
        result["noStress"] = from_union([to_float, from_none], self.no_stress)
        result["stress"] = from_union([to_float, from_none], self.stress)
        return result


@dataclass
class SpeechMessage:
    """Message for signaling state (changes) of speech IO (e.g. active/inactive)"""
    """flag for indicating, if speech input is active
    
    TODO more details needed? e.g. system-speech-output texts? more detailed state like IDLE,
    SPEECH_STARTED, etc? recognized speech/text?
    """
    data: Optional[bool]
    """the timestamp (including milliseconds) for the message"""
    timestamp: Optional[int]
    """type is "speechio" """
    type: Optional[MessageType]

    @staticmethod
    def from_dict(obj: Any) -> 'SpeechMessage':
        assert isinstance(obj, dict)
        data = from_union([from_bool, from_none], obj.get("data"))
        timestamp = from_union([from_int, from_none], obj.get("timestamp"))
        type = from_union([MessageType, from_none], obj.get("type"))
        return SpeechMessage(data, timestamp, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = from_union([from_bool, from_none], self.data)
        result["timestamp"] = from_union([from_int, from_none], self.timestamp)
        result["type"] = from_union([lambda x: to_enum(MessageType, x), from_none], self.type)
        return result


@dataclass
class ISpeechMessage:
    """Message for signaling state (changes) of speech IO (e.g. active/inactive)"""
    """flag for indicating, if speech input is active
    
    TODO more details needed? e.g. system-speech-output texts? more detailed state like IDLE,
    SPEECH_STARTED, etc? recognized speech/text?
    """
    data: Optional[bool]
    """the timestamp (including milliseconds) for the message"""
    timestamp: Optional[int]
    """type is "speechio" """
    type: Optional[MessageType]

    @staticmethod
    def from_dict(obj: Any) -> 'ISpeechMessage':
        assert isinstance(obj, dict)
        data = from_union([from_bool, from_none], obj.get("data"))
        timestamp = from_union([from_int, from_none], obj.get("timestamp"))
        type = from_union([MessageType, from_none], obj.get("type"))
        return ISpeechMessage(data, timestamp, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = from_union([from_bool, from_none], self.data)
        result["timestamp"] = from_union([from_int, from_none], self.timestamp)
        result["type"] = from_union([lambda x: to_enum(MessageType, x), from_none], self.type)
        return result


@dataclass
class ToggleSpeechMessage:
    """Message for signaling enabling/disabling speech IO (e.g. user pressed button for
    toggeling speech input)
    """
    """NA [TODO should this carry enabled/disabled information? then it would not be "toggled"
    but "set enabled"...]
    """
    data: Any
    """the timestamp (including milliseconds) for the message"""
    timestamp: Optional[int]
    """type is "togglespeech" """
    type: Optional[MessageType]

    @staticmethod
    def from_dict(obj: Any) -> 'ToggleSpeechMessage':
        assert isinstance(obj, dict)
        data = obj.get("data")
        timestamp = from_union([from_int, from_none], obj.get("timestamp"))
        type = from_union([MessageType, from_none], obj.get("type"))
        return ToggleSpeechMessage(data, timestamp, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = self.data
        result["timestamp"] = from_union([from_int, from_none], self.timestamp)
        result["type"] = from_union([lambda x: to_enum(MessageType, x), from_none], self.type)
        return result


@dataclass
class IToggleSpeechMessage:
    """Message for signaling enabling/disabling speech IO (e.g. user pressed button for
    toggeling speech input)
    """
    """NA [TODO should this carry enabled/disabled information? then it would not be "toggled"
    but "set enabled"...]
    """
    data: Any
    """the timestamp (including milliseconds) for the message"""
    timestamp: Optional[int]
    """type is "togglespeech" """
    type: Optional[MessageType]

    @staticmethod
    def from_dict(obj: Any) -> 'IToggleSpeechMessage':
        assert isinstance(obj, dict)
        data = obj.get("data")
        timestamp = from_union([from_int, from_none], obj.get("timestamp"))
        type = from_union([MessageType, from_none], obj.get("type"))
        return IToggleSpeechMessage(data, timestamp, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = self.data
        result["timestamp"] = from_union([from_int, from_none], self.timestamp)
        result["type"] = from_union([lambda x: to_enum(MessageType, x), from_none], self.type)
        return result


class ExerciseState(Enum):
    """the (unique) name of the exercise
    
    values for exercise state
    """
    COMPLETED = "COMPLETED"
    ENDED = "ENDED"
    PAUSED = "PAUSED"
    RESUMED = "RESUMED"
    STARTED = "STARTED"


@dataclass
class ExerciseData:
    """details for the session
    
    information/details about an exercise (session) and/or its state changes.
    
    details for the exercise
    """
    """the duration (in ms) for the exercise"""
    duration: Optional[int]
    """the ID for the exercise instantiation"""
    id: Optional[str]
    """the (unique) name of the exercise"""
    name: Optional[str]
    """if exercise was paused, duration of pause (in ms)"""
    pause_time: Optional[int]
    """the remaining time (in ms) for this exercise instantiation"""
    remaining_time: Optional[int]
    """the ID for the ("owning") session instantiation"""
    session_id: Optional[str]
    """the time (-stamp) when this exercise instantiation started"""
    start_time: Optional[int]
    """the (unique) name of the exercise"""
    state: Optional[ExerciseState]

    @staticmethod
    def from_dict(obj: Any) -> 'ExerciseData':
        assert isinstance(obj, dict)
        duration = from_union([from_int, from_none], obj.get("duration"))
        id = from_union([from_str, from_none], obj.get("id"))
        name = from_union([from_str, from_none], obj.get("name"))
        pause_time = from_union([from_int, from_none], obj.get("pauseTime"))
        remaining_time = from_union([from_int, from_none], obj.get("remainingTime"))
        session_id = from_union([from_str, from_none], obj.get("sessionId"))
        start_time = from_union([from_int, from_none], obj.get("startTime"))
        state = from_union([ExerciseState, from_none], obj.get("state"))
        return ExerciseData(duration, id, name, pause_time, remaining_time, session_id, start_time, state)

    def to_dict(self) -> dict:
        result: dict = {}
        result["duration"] = from_union([from_int, from_none], self.duration)
        result["id"] = from_union([from_str, from_none], self.id)
        result["name"] = from_union([from_str, from_none], self.name)
        result["pauseTime"] = from_union([from_int, from_none], self.pause_time)
        result["remainingTime"] = from_union([from_int, from_none], self.remaining_time)
        result["sessionId"] = from_union([from_str, from_none], self.session_id)
        result["startTime"] = from_union([from_int, from_none], self.start_time)
        result["state"] = from_union([lambda x: to_enum(ExerciseState, x), from_none], self.state)
        return result


@dataclass
class SessionMessage:
    """Message for signaling (state changes in) session"""
    """details for the session"""
    data: Optional[ExerciseData]
    """the timestamp (including milliseconds) for the message"""
    timestamp: Optional[int]
    """type is "session" """
    type: Optional[MessageType]

    @staticmethod
    def from_dict(obj: Any) -> 'SessionMessage':
        assert isinstance(obj, dict)
        data = from_union([ExerciseData.from_dict, from_none], obj.get("data"))
        timestamp = from_union([from_int, from_none], obj.get("timestamp"))
        type = from_union([MessageType, from_none], obj.get("type"))
        return SessionMessage(data, timestamp, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = from_union([lambda x: to_class(ExerciseData, x), from_none], self.data)
        result["timestamp"] = from_union([from_int, from_none], self.timestamp)
        result["type"] = from_union([lambda x: to_enum(MessageType, x), from_none], self.type)
        return result


@dataclass
class ISessionMessage:
    """Message for signaling (state changes in) session"""
    """details for the session"""
    data: Optional[ExerciseData]
    """the timestamp (including milliseconds) for the message"""
    timestamp: Optional[int]
    """type is "session" """
    type: Optional[MessageType]

    @staticmethod
    def from_dict(obj: Any) -> 'ISessionMessage':
        assert isinstance(obj, dict)
        data = from_union([ExerciseData.from_dict, from_none], obj.get("data"))
        timestamp = from_union([from_int, from_none], obj.get("timestamp"))
        type = from_union([MessageType, from_none], obj.get("type"))
        return ISessionMessage(data, timestamp, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = from_union([lambda x: to_class(ExerciseData, x), from_none], self.data)
        result["timestamp"] = from_union([from_int, from_none], self.timestamp)
        result["type"] = from_union([lambda x: to_enum(MessageType, x), from_none], self.type)
        return result


@dataclass
class IExerciseData:
    """information/details about an exercise (session) and/or its state changes."""
    """the duration (in ms) for the exercise"""
    duration: Optional[int]
    """the ID for the exercise instantiation"""
    id: Optional[str]
    """the (unique) name of the exercise"""
    name: Optional[str]
    """if exercise was paused, duration of pause (in ms)"""
    pause_time: Optional[int]
    """the remaining time (in ms) for this exercise instantiation"""
    remaining_time: Optional[int]
    """the ID for the ("owning") session instantiation"""
    session_id: Optional[str]
    """the time (-stamp) when this exercise instantiation started"""
    start_time: Optional[int]
    """the (unique) name of the exercise"""
    state: Optional[ExerciseState]

    @staticmethod
    def from_dict(obj: Any) -> 'IExerciseData':
        assert isinstance(obj, dict)
        duration = from_union([from_int, from_none], obj.get("duration"))
        id = from_union([from_str, from_none], obj.get("id"))
        name = from_union([from_str, from_none], obj.get("name"))
        pause_time = from_union([from_int, from_none], obj.get("pauseTime"))
        remaining_time = from_union([from_int, from_none], obj.get("remainingTime"))
        session_id = from_union([from_str, from_none], obj.get("sessionId"))
        start_time = from_union([from_int, from_none], obj.get("startTime"))
        state = from_union([ExerciseState, from_none], obj.get("state"))
        return IExerciseData(duration, id, name, pause_time, remaining_time, session_id, start_time, state)

    def to_dict(self) -> dict:
        result: dict = {}
        result["duration"] = from_union([from_int, from_none], self.duration)
        result["id"] = from_union([from_str, from_none], self.id)
        result["name"] = from_union([from_str, from_none], self.name)
        result["pauseTime"] = from_union([from_int, from_none], self.pause_time)
        result["remainingTime"] = from_union([from_int, from_none], self.remaining_time)
        result["sessionId"] = from_union([from_str, from_none], self.session_id)
        result["startTime"] = from_union([from_int, from_none], self.start_time)
        result["state"] = from_union([lambda x: to_enum(ExerciseState, x), from_none], self.state)
        return result


@dataclass
class ExerciseMessage:
    """Message for signaling (state changes in) exercises"""
    """details for the exercise"""
    data: Optional[ExerciseData]
    """the timestamp (including milliseconds) for the message"""
    timestamp: Optional[int]
    """type is "exercise" """
    type: Optional[MessageType]

    @staticmethod
    def from_dict(obj: Any) -> 'ExerciseMessage':
        assert isinstance(obj, dict)
        data = from_union([ExerciseData.from_dict, from_none], obj.get("data"))
        timestamp = from_union([from_int, from_none], obj.get("timestamp"))
        type = from_union([MessageType, from_none], obj.get("type"))
        return ExerciseMessage(data, timestamp, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = from_union([lambda x: to_class(ExerciseData, x), from_none], self.data)
        result["timestamp"] = from_union([from_int, from_none], self.timestamp)
        result["type"] = from_union([lambda x: to_enum(MessageType, x), from_none], self.type)
        return result


@dataclass
class IExerciseMessage:
    """Message for signaling (state changes in) exercises"""
    """details for the exercise"""
    data: Optional[ExerciseData]
    """the timestamp (including milliseconds) for the message"""
    timestamp: Optional[int]
    """type is "exercise" """
    type: Optional[MessageType]

    @staticmethod
    def from_dict(obj: Any) -> 'IExerciseMessage':
        assert isinstance(obj, dict)
        data = from_union([ExerciseData.from_dict, from_none], obj.get("data"))
        timestamp = from_union([from_int, from_none], obj.get("timestamp"))
        type = from_union([MessageType, from_none], obj.get("type"))
        return IExerciseMessage(data, timestamp, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = from_union([lambda x: to_class(ExerciseData, x), from_none], self.data)
        result["timestamp"] = from_union([from_int, from_none], self.timestamp)
        result["type"] = from_union([lambda x: to_enum(MessageType, x), from_none], self.type)
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


def hr_message_from_dict(s: Any) -> HrMessage:
    return HrMessage.from_dict(s)


def hr_message_to_dict(x: HrMessage) -> Any:
    return to_class(HrMessage, x)


def i_hr_message_from_dict(s: Any) -> IHrMessage:
    return IHrMessage.from_dict(s)


def i_hr_message_to_dict(x: IHrMessage) -> Any:
    return to_class(IHrMessage, x)


def stress_message_from_dict(s: Any) -> StressMessage:
    return StressMessage.from_dict(s)


def stress_message_to_dict(x: StressMessage) -> Any:
    return to_class(StressMessage, x)


def i_stress_message_from_dict(s: Any) -> IStressMessage:
    return IStressMessage.from_dict(s)


def i_stress_message_to_dict(x: IStressMessage) -> Any:
    return to_class(IStressMessage, x)


def stress_prediction_from_dict(s: Any) -> StressPrediction:
    return StressPrediction.from_dict(s)


def stress_prediction_to_dict(x: StressPrediction) -> Any:
    return to_class(StressPrediction, x)


def i_stress_prediction_from_dict(s: Any) -> IStressPrediction:
    return IStressPrediction.from_dict(s)


def i_stress_prediction_to_dict(x: IStressPrediction) -> Any:
    return to_class(IStressPrediction, x)


def speech_message_from_dict(s: Any) -> SpeechMessage:
    return SpeechMessage.from_dict(s)


def speech_message_to_dict(x: SpeechMessage) -> Any:
    return to_class(SpeechMessage, x)


def i_speech_message_from_dict(s: Any) -> ISpeechMessage:
    return ISpeechMessage.from_dict(s)


def i_speech_message_to_dict(x: ISpeechMessage) -> Any:
    return to_class(ISpeechMessage, x)


def toggle_speech_message_from_dict(s: Any) -> ToggleSpeechMessage:
    return ToggleSpeechMessage.from_dict(s)


def toggle_speech_message_to_dict(x: ToggleSpeechMessage) -> Any:
    return to_class(ToggleSpeechMessage, x)


def i_toggle_speech_message_from_dict(s: Any) -> IToggleSpeechMessage:
    return IToggleSpeechMessage.from_dict(s)


def i_toggle_speech_message_to_dict(x: IToggleSpeechMessage) -> Any:
    return to_class(IToggleSpeechMessage, x)


def session_message_from_dict(s: Any) -> SessionMessage:
    return SessionMessage.from_dict(s)


def session_message_to_dict(x: SessionMessage) -> Any:
    return to_class(SessionMessage, x)


def i_session_message_from_dict(s: Any) -> ISessionMessage:
    return ISessionMessage.from_dict(s)


def i_session_message_to_dict(x: ISessionMessage) -> Any:
    return to_class(ISessionMessage, x)


def exercise_data_from_dict(s: Any) -> ExerciseData:
    return ExerciseData.from_dict(s)


def exercise_data_to_dict(x: ExerciseData) -> Any:
    return to_class(ExerciseData, x)


def i_exercise_data_from_dict(s: Any) -> IExerciseData:
    return IExerciseData.from_dict(s)


def i_exercise_data_to_dict(x: IExerciseData) -> Any:
    return to_class(IExerciseData, x)


def exercise_state_from_dict(s: Any) -> ExerciseState:
    return ExerciseState(s)


def exercise_state_to_dict(x: ExerciseState) -> Any:
    return to_enum(ExerciseState, x)


def exercise_message_from_dict(s: Any) -> ExerciseMessage:
    return ExerciseMessage.from_dict(s)


def exercise_message_to_dict(x: ExerciseMessage) -> Any:
    return to_class(ExerciseMessage, x)


def i_exercise_message_from_dict(s: Any) -> IExerciseMessage:
    return IExerciseMessage.from_dict(s)


def i_exercise_message_to_dict(x: IExerciseMessage) -> Any:
    return to_class(IExerciseMessage, x)


def error_message_from_dict(s: Any) -> ErrorMessage:
    return ErrorMessage.from_dict(s)


def error_message_to_dict(x: ErrorMessage) -> Any:
    return to_class(ErrorMessage, x)


def i_error_message_from_dict(s: Any) -> IErrorMessage:
    return IErrorMessage.from_dict(s)


def i_error_message_to_dict(x: IErrorMessage) -> Any:
    return to_class(IErrorMessage, x)
