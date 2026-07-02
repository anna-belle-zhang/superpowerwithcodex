# Browser Companion Assets Delta Spec

## ADDED

### Visual companion operating guide
GIVEN `skills/brainstorming/visual-companion.md` exists
WHEN an agent reads the guide
THEN it explains when to use the browser versus terminal
AND explains how to start the server, write screens, read events, iterate, and stop the server

### Frame template provides selectable option UI
GIVEN an HTML fragment contains elements with `data-choice`
WHEN the server wraps the fragment with `frame-template.html`
THEN the page includes selectable option styling
AND includes a visible selection indicator area
AND preserves the fragment content

### Helper script posts browser selections
GIVEN a wrapped browser screen is open
WHEN the user clicks an option with `data-choice`
THEN `helper.js` records the selected choice
AND sends a JSON event to the server over WebSocket

### Helper script supports reload messages
GIVEN a wrapped browser screen is open
AND the browser is connected over WebSocket
WHEN the server sends a reload message
THEN `helper.js` reloads the page so the newest screen is shown

### Content fragments are the default authoring format
GIVEN an agent writes a visual brainstorming screen
WHEN complete page control is not required
THEN the agent writes an HTML fragment without `<html>`, `<head>`, or framework boilerplate
AND relies on the server to wrap the fragment

### Unique screen filenames are required
GIVEN the agent writes multiple visual brainstorming screens in one session
WHEN a new screen or revision is created
THEN the agent writes it to a new semantic filename
AND does not reuse the previous screen filename

### Project session artifacts are gitignored
GIVEN the visual companion is launched with `--project-dir "$PWD"` from the repository root
WHEN session files are written under `.superpowers/brainstorm/`
THEN git status does not show those session files as untracked
