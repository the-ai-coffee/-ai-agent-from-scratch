"""Agent-003: Conversation History.

Same read-act-repeat loop as agent-002, but the agent now remembers the
conversation. Instead of sending each line on its own, it keeps a growing
`messages` list -- every user line and every reply is appended -- and sends
the whole history to Claude on each turn. That history is what turns a
stateless responder into something that can follow a conversation.
"""

import sys

from anthropic import Anthropic

MODEL = "claude-haiku-4-5-20251001"


def run(input_stream, output_stream, client=None):
    """Read lines from input_stream, send the running history, write the reply.

    Stops on EOF or on the first empty line.
    """
    client = client or Anthropic()
    messages = []

    while True:
        output_stream.write("User> ")
        output_stream.flush()
        line = input_stream.readline()
        if not line:
            break
        line = line.rstrip("\n")
        if not line:
            break
        messages.append({"role": "user", "content": line})
        message = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=messages,
        )
        reply = message.content[0].text
        messages.append({"role": "assistant", "content": reply})
        output_stream.write(f"Agent> {reply}\n")


if __name__ == "__main__":
    # Force UTF-8 on the terminal streams so accented characters and
    # non-breaking spaces decode correctly even under a C/POSIX locale.
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")
    sys.stdout.reconfigure(encoding="utf-8")
    run(sys.stdin, sys.stdout)
