# Roadmap: Agent-001 through Agent-012

## Context

This repo is a staged series of self-contained agent folders, each adding
exactly one new mechanism on top of the last, paired with a blog post.
CLAUDE.md states the destination: "agents with LLM calls, tools, and
evals." This roadmap lays out the full path there, stage by stage, with no
stage covering more than one new mechanism.

## Stages

1. **agent-001: echo-loop** -- *(built)* The bare read-act-repeat loop,
   no LLM: every input line is the observation, echoing it back is the
   action.

2. **agent-002: llm-call** -- *(built)* Same loop; the action is now a
   single stateless `messages.create` call. Each line is sent on its own,
   with no memory of earlier lines.

3. **agent-003: conversation-history (short-term memory)** -- Stop
   sending each line in isolation; accumulate a `messages` list across
   turns and pass the whole list to every `messages.create` call. First
   time the agent has memory of what was said earlier -- in-context,
   lossless within the session, gone once the process ends. This is the
   deliberate counterpart to agent-007's long-term memory (RAG):
   short-term memory is "everything said so far, kept verbatim in
   context"; long-term memory is "facts retrieved on demand from outside
   context." Test: two-turn exchange where the second reply depends on
   the first, using a fake client that asserts on the message list it
   received.

4. **agent-004: system-prompt** -- Introduce a `system` parameter so the
   agent has configurable persona/instructions, separate from
   conversation turns. Test: fake client asserts the `system` kwarg is
   passed through unchanged.

5. **agent-005: single-tool-call** -- Give the model one tool via
   `tools`, detect a `tool_use` block in the response, execute the
   corresponding Python function, and print the result. No loop-back to
   the model yet -- this stage is just "the model can ask for a tool and
   we run it." Test: fake client returns a canned `tool_use` block;
   assert the right function ran with the right args.

6. **agent-006: tool-result-loop** -- Close the loop: append the tool's
   result to the message list and call the model again so it can use the
   result to produce a final natural-language answer. First stage with
   genuine multi-step agentic behavior (call -> tool -> call -> answer).
   This is the mechanism RAG (next stage) plugs into. Test: fake client
   scripted to return `tool_use` on call 1 and text on call 2; assert the
   loop terminates after the right number of calls.

7. **agent-007: RAG (long-term memory)** -- Let the agent search
   documents/a knowledge base instead of relying only on what's in
   context. Covers: what an embedding is (simple conceptual treatment),
   a minimal in-memory vector store built with `numpy` (cosine
   similarity over a handful of stored chunks), and wiring that search up
   as a tool through the loop built in agent-006. Test: fake embedding
   function and a small fixed corpus; assert the right chunk is
   retrieved and passed back as a tool_result for a given query.

8. **agent-008: multi-tool-dispatch** -- The agent now has two tools
   (RAG search from agent-007, plus one more -- e.g. a calculator) so
   this is the first point a registry actually earns its keep. Generalize
   from a single hardcoded tool to a dict of name -> function + schema;
   covers the model choosing among tools, including choosing none. Test:
   fake client picks tool B; assert dispatch calls B's function, not A's.

9. **agent-009: malformed-tool-call-handling** -- Tool calls can come
   back with invalid JSON args, an unknown tool name, or a tool that
   raises. Add minimal handling for each (catch, report back to the
   model as a `tool_result` with `is_error`, let the model retry or
   apologize) instead of crashing the loop. Test: each of the three
   failure modes, asserting the loop survives and feeds an error
   tool_result back.

10. **agent-010: persistent-session** -- Save/load the conversation
    history to/from disk (e.g. JSON) so a session survives process
    restart. Keeps the in-memory `messages` list as the source of truth
    during a run; adds load-at-start / save-at-exit. Test: write a
    transcript, restart `run` with a fresh process equivalent, assert
    prior turns are present.

11. **agent-011: evals-and-tracing** -- Two things that belong together
    because they answer the same question -- "what is the agent actually
    doing?":
    - A clean log of thought-vs-action at each loop turn (plain logging,
      no tracing framework -- prompt-tracking basics only).
    - A small eval harness: scripted conversations with expected
      properties ("must call tool X", "must not call any tool", "final
      answer contains Y"), run against a fake/recorded client, with
      pass/fail output.
    First stage that checks the agent's *behavior* rather than its
    mechanics; the logging makes failures legible when an eval fails.

12. **agent-012: capstone** -- No new mechanism. A closing demo that
    exercises everything built so far in one run (search a topic via
    RAG, synthesize an answer, call a tool), plus a written comparison
    against LangGraph/CrewAI/AutoGen now that the reader has built the
    same pieces by hand and can evaluate what those frameworks are
    actually doing for them.
