---
name: gemini-cli
description: Use when user requests Gemini to analyze multimodal content (images, PDFs, audio, video), process long documents, or scan large codebases - dispatches to gemini-executor agent for isolated execution
---

# Gemini CLI Integration

Dispatch Gemini CLI for multimodal analysis and ultra-long context tasks while keeping main conversation clean.

## When to Use

Trigger when user mentions:
- "Use Gemini to analyze [file/image/video/audio]"
- "Let Gemini scan this project/directory"
- "Gemini help me [summarize/extract/understand] [document]"
- "Ask Gemini about [long content]"
- Any request for multimodal analysis (images, PDFs, audio, video)
- Any request involving ultra-long context (large codebases, long documents)

## Core Principle

**Thin Skill + Thick Executor:**
- **Skill (this file):** Recognizes intent, validates request, dispatches to executor
- **Executor (agent):** Runs Gemini CLI, processes output, returns summary

**Context Isolation:**
Gemini's output can be thousands of lines. The executor agent isolates this from the main conversation - you only see the summary.

## Workflow

### Step 1: Recognize Intent and Validate

When user requests Gemini analysis:

1. **Identify what to analyze:**
   - File path(s): ~/Documents/report.pdf, screenshot.png
   - Directory: ./src (use --all-files)
   - Content type: image, PDF, audio, video, code

2. **Validate:**
   - Files exist and are accessible
   - Gemini CLI is installed (gemini --version)
   - Request is appropriate for Gemini (multimodal or long context)

3. **Extract prompt:**
   - User's question or task
   - What they want to know/extract/understand

### Step 2: Dispatch to Agent

Use the Task tool with general-purpose agent:

Task: Execute Gemini CLI analysis

User Request: [Original request]
Prompt for Gemini: [Extracted prompt]
Files to analyze: [Paths or --all-files]

Expected output:
- Summary of key findings (3-5 bullets)
- Answer to user's question
- Important details or insights

Gemini CLI Command:
- For files: gemini -p "prompt" file1 file2 --yolo
- For directory: cd <dir> && gemini --all-files -p "prompt" --yolo

Important:
- Always use --yolo flag (non-interactive)
- Return concise summary (not raw output)
- Extract key points only

### Step 3: Return Summary to User

When agent returns:

1. **Present findings concisely:**
   - Answer user's question directly
   - 3-5 key points
   - Relevant excerpts/quotes

2. **Offer follow-up:**
   - More detail on specific points
   - Additional file analysis

## Example Interactions

### Example 1: Image Analysis

User: Use Gemini to analyze this screenshot
Assistant: *Dispatches agent with gemini -p "analyze UI" screenshot.png --yolo*
Assistant: Gemini analyzed the screenshot. Key findings:
- Layout uses inconsistent spacing (mix of 8px and 12px)
- Color contrast ratio 3.2:1 (below WCAG 4.5:1 standard)
- CTA button lacks visual hierarchy
- Navigation menu hidden on mobile

Would you like Gemini to suggest specific improvements?

### Example 2: PDF Document

User: Gemini help me summarize this research paper docs/paper.pdf
Assistant: *Dispatches agent*
Assistant: Summary of paper.pdf:
- Proposes new neural architecture for time-series prediction
- Achieves 15% improvement over LSTM baseline
- Tested on 3 public datasets (weather, stock, traffic)
- Main limitation: requires large training data (>10K samples)

Would you like me to ask Gemini for more detail on methodology?

### Example 3: Codebase Scan

User: Let Gemini scan ./src and identify potential security issues
Assistant: *Dispatches with gemini --all-files -p "identify security issues" --yolo*
Assistant: Gemini scanned 47 files. Security findings:
- SQL injection risk in api/database.py:45 (unsanitized input)
- Hardcoded API key in config/settings.py:12
- Missing input validation on user uploads (files.py)
- Password stored in plain text (auth.py:78)

I can help fix these issues. Which should we address first?

## Best Practices

**Always use --yolo:**
Non-interactive contexts MUST include --yolo or commands hang waiting for user confirmation.

**Prefer --all-files for code:**
Let Gemini read files directly rather than cat-ing content into prompts.

**Use heredoc for long prompts:**
Avoid command-line escaping issues.

**Return summaries, not raw output:**
Extract key points (3-5 bullets) for main conversation.

**Don't send sensitive data:**
Warn user if files might contain secrets/credentials before sending to external API.

## When NOT to Use

**Don't use Gemini for:**
- Tasks Claude can handle natively (code editing, file operations)
- Quick questions that don't need multimodal/long-context
- Sensitive data without user confirmation
- Tasks requiring file modification (Gemini is read-only analysis)

**Use Claude directly for:**
- Code implementation
- File editing
- Git operations
- Test writing
- Short document analysis

## Integration with Other Skills

**Pairs well with:**
- @superpowers:brainstorming - Use Gemini for research phase
- @superpowers:code-reviewer - Gemini analyzes, Claude reviews
- @superpowers:systematic-debugging - Gemini scans logs, Claude debugs

**Typical workflow:**
1. User asks to analyze large/multimodal content
2. This skill dispatches Gemini for analysis
3. Return summary to main conversation
4. Use other skills to act on findings (implement, fix, refactor)

## Troubleshooting

**"gemini: command not found"**
- Install Gemini CLI first
- Verify with: gemini --version

**Command hangs/blocks:**
- Missing --yolo flag
- Add --yolo to all non-interactive commands

**Output too long:**
- Agent should extract key points only
- If raw output returned, re-prompt for summary

**File not found:**
- Verify file paths are absolute or relative to current directory
- Check file permissions
