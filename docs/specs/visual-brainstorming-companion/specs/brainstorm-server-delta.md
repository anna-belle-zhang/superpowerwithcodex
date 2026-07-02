# Brainstorm Server Delta Spec

## ADDED

### Project session startup
GIVEN `skills/brainstorming/scripts/start-server.sh --project-dir "$PWD"` is run from the repository root
WHEN the server starts successfully
THEN stdout contains a JSON object with `type: "server-started"`, `url`, `screen_dir`, and `state_dir`
AND `screen_dir` is under the repository's `.superpowers/brainstorm/` directory and ends with `/content`
AND `state_dir` is under the same session directory and ends with `/state`

### Server info persistence
GIVEN the brainstorm server has started
WHEN startup completes
THEN the same connection JSON is written to `state_dir/server-info`
AND the JSON can be read by a later agent turn without relying on captured stdout

### Waiting page when no screens exist
GIVEN the brainstorm server is running
AND no `.html` files exist in `screen_dir`
WHEN a browser requests `/`
THEN the server returns HTTP 200
AND the response contains a waiting page for the agent to push a screen

### Content fragment wrapping
GIVEN the server is running
AND `screen_dir` contains a newest `.html` file that does not start with `<!DOCTYPE` or `<html`
WHEN a browser requests `/`
THEN the server wraps the fragment in `frame-template.html`
AND injects `helper.js`
AND returns the result as `text/html`

### Full document serving
GIVEN the server is running
AND `screen_dir` contains a newest `.html` file that starts with `<!DOCTYPE` or `<html`
WHEN a browser requests `/`
THEN the server serves the document without wrapping it in the frame template
AND still injects `helper.js`

### Newest screen selection
GIVEN `screen_dir` contains multiple `.html` files
WHEN a browser requests `/`
THEN the server serves the `.html` file with the newest modification time
AND ignores newer non-HTML files for screen selection

### Static file serving
GIVEN `screen_dir` contains an asset file
WHEN a browser requests that asset through the `/files/` route
THEN the server returns the file if it exists
AND returns 404 if it does not exist

### WebSocket choice recording
GIVEN a browser client is connected over WebSocket
WHEN the client sends a valid JSON event containing a `choice` property
THEN the server appends the event as one JSON line to `state_dir/events`
AND logs the event to stdout with `source: "user-event"`

### Non-choice events are not persisted
GIVEN a browser client is connected over WebSocket
WHEN the client sends a valid JSON event without a `choice` property
THEN the event is logged to stdout
AND `state_dir/events` is not created or appended for that event

### New screen clears prior choices
GIVEN `state_dir/events` exists from a previous screen
WHEN a new `.html` file appears in `screen_dir`
THEN the server deletes `state_dir/events`
AND broadcasts a reload event to connected browser clients

### File changes reload connected clients
GIVEN one or more browser clients are connected over WebSocket
WHEN an existing `.html` screen changes
THEN every connected client receives a reload message
AND the server logs a screen update event

### Malformed browser event handling
GIVEN a browser client is connected over WebSocket
WHEN the client sends malformed JSON
THEN the server logs an error
AND continues serving HTTP and WebSocket clients

### Zero runtime dependencies
GIVEN the brainstorm server files are installed
WHEN `server.cjs` is inspected or executed
THEN runtime behavior uses only Node.js built-in modules
AND no runtime `node_modules` installation is required

### Stop server lifecycle
GIVEN a brainstorm session directory contains `state/server.pid`
WHEN `skills/brainstorming/scripts/stop-server.sh` is run with that session directory path
THEN the process is terminated if still running
AND `/tmp` session directories are removed
AND project `.superpowers/brainstorm/` session directories are preserved
