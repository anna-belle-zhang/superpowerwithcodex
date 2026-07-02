# Brainstorm Server Tests Delta Spec

## ADDED

### Server startup tests
GIVEN the brainstorm server test suite is installed
WHEN `npm test --prefix tests/brainstorm-server` runs
THEN it verifies startup JSON on stdout
AND verifies `state/server-info` is written with `screen_dir` and `state_dir`

### HTTP serving tests
GIVEN the brainstorm server test suite is running
WHEN HTTP serving tests execute
THEN they verify the waiting page, full document serving, fragment wrapping, newest HTML selection, ignored non-HTML files, content type, and 404 behavior

### WebSocket event tests
GIVEN the brainstorm server test suite is running
WHEN WebSocket tests execute
THEN they verify upgrade handling, user event logging, choice persistence, non-choice filtering, malformed JSON resilience, and multiple concurrent clients

### File watching tests
GIVEN the brainstorm server test suite is running
WHEN file watching tests execute
THEN they verify reload broadcasts for new and changed HTML screens
AND verify non-HTML files do not trigger screen reload behavior
AND verify previous choice events are cleared when a new screen is added

### Asset contract tests
GIVEN the brainstorm server test suite is running
WHEN asset verification tests execute
THEN they verify `helper.js` exposes the required browser APIs
AND verify `frame-template.html` contains the required frame structure and content placeholder

### Test-only WebSocket dependency
GIVEN the brainstorm server tests use a WebSocket client library
WHEN dependencies are installed for `tests/brainstorm-server`
THEN the `ws` package is installed only for tests
AND the runtime brainstorm server remains dependency-free
