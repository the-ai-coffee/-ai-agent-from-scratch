import io
from dataclasses import dataclass

from agent import calculator, run


@dataclass
class FakeTextBlock:
    text: str
    type: str = "text"


@dataclass
class FakeToolUseBlock:
    id: str
    name: str
    input: dict
    type: str = "tool_use"


@dataclass
class FakeMessage:
    content: list
    stop_reason: str
    role: str = "assistant"


class FakeMessages:
    """Returns scripted responses in order, recording each call's arguments."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(
            {"system": kwargs.get("system"), "messages": list(kwargs["messages"])}
        )
        return self.responses.pop(0)


class FakeClient:
    def __init__(self, responses):
        self.messages = FakeMessages(responses)


def text_reply(text):
    return FakeMessage(content=[FakeTextBlock(text=text)], stop_reason="end_turn")


def tool_call(expression, tool_id="t1"):
    return FakeMessage(
        content=[FakeToolUseBlock(id=tool_id, name="calculator", input={"expression": expression})],
        stop_reason="tool_use",
    )


def test_plain_text_reply():
    client = FakeClient([text_reply("hi there")])
    output_stream = io.StringIO()

    run(io.StringIO("hello\n"), output_stream, client=client)

    assert output_stream.getvalue() == "User> Agent> hi there\nUser> "


def test_tool_call_is_run_and_shown():
    client = FakeClient([tool_call("2 + 3")])
    output_stream = io.StringIO()

    run(io.StringIO("what is 2 + 3?\n"), output_stream, client=client)

    output = output_stream.getvalue()
    assert "[tool] calculator({'expression': '2 + 3'}) -> 5\n" in output
    assert "Agent> 5\n" in output


def test_tool_turn_is_not_kept_in_history():
    # A tool turn followed by a text turn: the second call's history must be
    # clean -- the dangling tool request is dropped, not carried forward.
    client = FakeClient([tool_call("2 + 3"), text_reply("hello again")])
    output_stream = io.StringIO()

    run(io.StringIO("what is 2 + 3?\nhi\n"), output_stream, client=client)

    assert client.messages.calls[1]["messages"] == [{"role": "user", "content": "hi"}]


def test_text_history_accumulates_across_turns():
    client = FakeClient([text_reply("first reply"), text_reply("second reply")])
    output_stream = io.StringIO()

    run(io.StringIO("first\nsecond\n"), output_stream, client=client)

    assert client.messages.calls[1]["messages"] == [
        {"role": "user", "content": "first"},
        {"role": "assistant", "content": "first reply"},
        {"role": "user", "content": "second"},
    ]


def test_system_prompt_is_sent():
    client = FakeClient([text_reply("ok")])

    run(io.StringIO("hi\n"), io.StringIO(), client=client, system="be terse")

    assert client.messages.calls[0]["system"] == "be terse"


def test_calculator_evaluates_arithmetic():
    assert calculator("2 + 2 * 3") == "8"
    assert calculator("(1 + 2) * 3") == "9"
    assert calculator("-4 / 2") == "-2.0"


def test_calculator_rejects_unsafe_input():
    assert calculator("__import__('os').system('echo hi')").startswith("Error")
    assert calculator("1 / 0").startswith("Error")
