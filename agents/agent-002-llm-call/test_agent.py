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
    def create(self, **kwargs):
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
