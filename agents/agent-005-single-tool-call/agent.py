"""Agent-005: Single Tool Call.

Builds on agent-004. For the first time the agent can *act*, not just talk. We
hand the model one tool -- a calculator -- and let it decide when it's needed.
When the model asks for the tool, we detect the request, run our code, and show
the result.

This stage stops there, on purpose. The model asks; we run it; we print what
came back. We do **not** yet hand the result back to the model so it can fold
it into a sentence -- that's the loop we close in agent-006. Seeing the gap is
the whole point: here you watch the agent reach for a tool, but it can't yet
talk about what it found.
"""

import ast
import operator
import sys

from anthropic import Anthropic

MODEL = "claude-haiku-4-5-20251001"

SYSTEM_PROMPT = (
    "You are a concise, friendly assistant. When a question needs arithmetic, "
    "use the calculator tool instead of working it out yourself."
)

# The single tool we advertise. This is just a description -- the model never
# runs anything itself; it can only ask us to. The input_schema tells the model
# what arguments the tool expects.
TOOLS = [
    {
        "name": "calculator",
        "description": (
            "Evaluate a basic arithmetic expression and return the result. "
            "Supports +, -, *, /, and parentheses."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The expression to evaluate, e.g. '2 + 2 * 3'.",
                }
            },
            "required": ["expression"],
        },
    }
]

# Only these operators are allowed, so evaluating an expression can never run
# arbitrary code -- it just does arithmetic.
_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_eval_node(node.operand))
    raise ValueError("unsupported expression")


def calculator(expression):
    """Safely evaluate an arithmetic expression and return its result as text."""
    try:
        return str(_eval_node(ast.parse(expression, mode="eval").body))
    except (ValueError, SyntaxError, ZeroDivisionError, TypeError) as error:
        return f"Error: {error}"


def run_tool(name, tool_input):
    """Dispatch a tool call by name. Returns the tool's text result."""
    if name == "calculator":
        return calculator(tool_input["expression"])
    return f"Error: unknown tool {name!r}"


def run(input_stream, output_stream, client=None, system=SYSTEM_PROMPT):
    """Read lines; let Claude answer in text or ask for the tool; write output.

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
            system=system,
            tools=TOOLS,
            messages=messages,
        )

        if message.stop_reason == "tool_use":
            # The model asked for the tool. Find the request, run it, show it.
            tool_use = next(b for b in message.content if b.type == "tool_use")
            result = run_tool(tool_use.name, tool_use.input)
            output_stream.write(
                f"[tool] {tool_use.name}({tool_use.input}) -> {result}\n"
            )
            # The best we can do right now is hand back the raw result -- the
            # model never saw it, so it can't phrase a reply.
            output_stream.write(f"Agent> {result}\n")
            # We don't record this turn: a tool request with no result fed back
            # would break the next call, and the model isn't part of this
            # exchange yet. Threading it into the conversation is agent-006.
            messages.pop()
            continue

        reply = message.content[0].text
        messages.append({"role": "assistant", "content": reply})
        output_stream.write(f"Agent> {reply}\n")


if __name__ == "__main__":
    # Force UTF-8 on the terminal streams so accented characters and
    # non-breaking spaces decode correctly even under a C/POSIX locale.
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")
    sys.stdout.reconfigure(encoding="utf-8")
    run(sys.stdin, sys.stdout)
