"""Agent-002: LLM Call.

Same read-act-repeat loop as agent-001, but the "act" step is now a real
LLM call instead of an echo. Each line is sent to Claude independently --
no conversation history is kept between turns.
"""

import sys

from anthropic import Anthropic

MODEL = "claude-haiku-4-5-20251001"


def run(input_stream, output_stream, client=None):
    """Read lines from input_stream, send each to Claude, write the reply.

    Stops on EOF or on the first empty line.
    """
    client = client or Anthropic()

    while True:
        output_stream.write("User> ")
        output_stream.flush()
        line = input_stream.readline()
        if not line:
            break
        line = line.rstrip("\n")
        if not line:
            break
        message = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": line}],
        )
        output_stream.write(f"Agent> {message.content[0].text}\n")


if __name__ == "__main__":
    run(sys.stdin, sys.stdout)
