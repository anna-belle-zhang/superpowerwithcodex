# Visual Brainstorming Companion Design

## Architecture

Import upstream's visual brainstorming companion as a focused addition to the existing
brainstorming skill. The browser companion is a local HTTP/WebSocket server started by
shell scripts inside `skills/brainstorming/scripts/`. The skill decides when the
browser is useful, starts the server when the user accepts, writes HTML fragments to a
session content directory, and reads browser interaction events from a session state
directory.

The implementation must not replace this fork's brainstorming workflow wholesale. This
fork already adds a deep survey step that gathers local and external context after the
purpose is understood. The visual companion should sit before clarifying questions as an
optional tool, while the deep survey remains before approach selection.

## Components

| Component | Responsibility |
|-----------|----------------|
| `skills/brainstorming/SKILL.md` | Describes when to offer the companion and how it fits into the brainstorming flow |
| `skills/brainstorming/visual-companion.md` | Detailed operating guide for starting the server, writing screens, reading events, and cleaning up |
| `skills/brainstorming/scripts/start-server.sh` | Creates a session directory and starts `server.cjs` in foreground or background mode |
| `skills/brainstorming/scripts/stop-server.sh` | Stops a session server and cleans up only ephemeral `/tmp` sessions |
| `skills/brainstorming/scripts/server.cjs` | Zero-dependency HTTP/WebSocket server using Node.js built-ins |
| `skills/brainstorming/scripts/frame-template.html` | Browser frame, CSS, and content placeholder for HTML fragments |
| `skills/brainstorming/scripts/helper.js` | Client-side reload, click, and event-posting helper |
| `tests/brainstorm-server/` | Focused tests for server protocol, HTTP behavior, file watching, and lifecycle behavior |

## Data Flow

1. During brainstorming, the agent identifies that upcoming questions may be visual.
2. The agent offers the companion in a standalone message and waits for consent.
3. If accepted, the agent starts `start-server.sh --project-dir "$PWD"` from the
   repository root.
4. The script creates a unique session directory under `.superpowers/brainstorm/`
   with `content/` and `state/` child directories.
5. `server.cjs` writes startup JSON to stdout and `state/server-info`.
6. The agent writes a new `.html` file to `content/` for each visual screen.
7. The server serves the newest HTML file and reloads connected browser clients.
8. Browser interactions are sent over WebSocket and recorded as JSON lines in
   `state/events` when they include a `choice`.
9. On the next user turn, the agent reads `state/events` and combines it with the user's
   terminal feedback.

## Error Handling

| Scenario | Handling |
|----------|---------|
| User declines companion | Continue text-only brainstorming |
| Server cannot start within timeout | Print JSON error and continue with terminal-only brainstorming unless user wants to retry |
| Background process is reaped | `start-server.sh` detects likely environments and can run foreground mode |
| No HTML screens exist | Server returns a waiting page |
| Browser sends malformed JSON | Server logs to stderr and continues |
| WebSocket receives unsupported opcode | Server closes that connection without crashing |
| `state/server-info` disappears | Agent restarts the server before writing new visual screens |

## Dependencies

- Runtime: Node.js only, using built-in `http`, `crypto`, `fs`, and `path` modules.
- Test-only: `ws` package in `tests/brainstorm-server/package.json`.
- Shell: Bash for `start-server.sh` and `stop-server.sh`.

## Testing Strategy

The implementation should import upstream's `tests/brainstorm-server` suite and run it
after adapting paths. The test suite should cover:

- server startup JSON and `state/server-info`;
- waiting page behavior;
- full HTML document serving;
- fragment wrapping with `frame-template.html`;
- newest-file selection;
- WebSocket event relay;
- `state/events` writing and clearing;
- reload broadcast on HTML changes;
- helper and frame template required APIs.

Manual smoke testing should start the server from the repo root, open the returned URL,
write a simple HTML fragment to `screen_dir`, click an option, and verify that
`state_dir/events` contains the choice.
