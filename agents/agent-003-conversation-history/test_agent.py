import io
from dataclasses import dataclass

from agent import run


@dataclass
class FakeContentBlock:
    text: str


@dataclass
class FakeMessage:
    content: list


class FakeMessages:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        # Record a copy of the history sent on each call so tests can inspect
        # how it grows between turns.
        self.calls.append(list(kwargs["messages"]))
        return FakeMessage(content=[FakeContentBlock(text="fake reply")])


class FakeClient:
    def __init__(self):
        self.messages = FakeMessages()


def test_replies_to_input_lines():
    input_stream = io.StringIO("hello\n")
    output_stream = io.StringIO()

    run(input_stream, output_stream, client=FakeClient())

    assert output_stream.getvalue() == "User> Agent> fake reply\nUser> "


def test_stops_on_empty_line():
    input_stream = io.StringIO("hello\n\n")
    output_stream = io.StringIO()

    run(input_stream, output_stream, client=FakeClient())

    assert output_stream.getvalue() == "User> Agent> fake reply\nUser> "


def test_stops_on_eof_with_no_trailing_newline():
    input_stream = io.StringIO("hello")
    output_stream = io.StringIO()

    run(input_stream, output_stream, client=FakeClient())

    assert output_stream.getvalue() == "User> Agent> fake reply\nUser> "


def test_history_accumulates_across_turns():
    input_stream = io.StringIO("first\nsecond\n")
    output_stream = io.StringIO()
    client = FakeClient()

    run(input_stream, output_stream, client=client)

    # First turn sends just the first user line.
    assert client.messages.calls[0] == [
        {"role": "user", "content": "first"},
    ]
    # Second turn carries the first exchange plus the new line.
    assert client.messages.calls[1] == [
        {"role": "user", "content": "first"},
        {"role": "assistant", "content": "fake reply"},
        {"role": "user", "content": "second"},
    ]
