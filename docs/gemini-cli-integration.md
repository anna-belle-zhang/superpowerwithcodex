# Gemini CLI Integration Guide

Complete guide to using Gemini CLI with Superpowers for multimodal analysis and ultra-long context tasks.

---

## Overview

**What this integration provides:**
- Analyze images, PDFs, audio, video through Gemini
- Process ultra-long documents and codebases
- Context isolation: Gemini's long output doesn't pollute main conversation
- Thin skill + thick executor pattern for clean integration

**Architecture:**
```
User Request
    ↓
Gemini CLI Skill (intent recognition)
    ↓
General-Purpose Agent (execution)
    ↓
Gemini CLI (analysis)
    ↓
Summary → Main Conversation
```

---

## Prerequisites

### 1. Install Gemini CLI

```bash
# Installation method depends on Gemini CLI distribution
# Check official docs for latest instructions
gemini --version  # Verify installation
```

### 2. Configure Gemini

```bash
# Authenticate if required
gemini login

# Verify free tier quota
gemini quota
```

### 3. Install Superpowers

```bash
claude plugin install superpowers@superpowerwithcodex --scope project
```

---

## Quick Start

### Example 1: Analyze an Image

```bash
# In Claude Code session
User: Use Gemini to analyze this screenshot and suggest UI improvements
      ~/Downloads/app-screenshot.png
```

**What happens:**
1. `gemini-cli` skill recognizes intent
2. Validates file exists
3. Dispatches general-purpose agent with task
4. Agent runs: `gemini -p "analyze UI and suggest improvements" ~/Downloads/app-screenshot.png --yolo`
5. Gemini analyzes (potentially 100+ lines of output)
6. Agent extracts key findings (3-5 bullets)
7. Summary returned to you

**You receive:**
```
Gemini analyzed app-screenshot.png. Key UI improvements needed:

- Inconsistent spacing (mix of 8px, 12px, 16px margins)
- Low color contrast (3.2:1 ratio, needs 4.5:1 for WCAG AA)
- Weak visual hierarchy (all text same weight)
- CTA button lacks emphasis
- Mobile navigation hidden

Would you like me to help implement these improvements?
```

### Example 2: Summarize a PDF

```bash
User: Gemini help me summarize this research paper
      docs/research-paper.pdf
```

**You receive:**
```
Gemini summarized research-paper.pdf:

- Proposes "TemporalNet" architecture for time-series prediction
- Achieves 15% accuracy improvement over LSTM baseline
- Tested on weather, stock prices, and traffic datasets
- Main limitation: requires 10K+ training samples
- Key innovation: Attention mechanism for dynamic historical weighting

Would you like me to ask Gemini for more detail on methodology?
```

### Example 3: Scan Codebase for Security Issues

```bash
User: Let Gemini scan ./src and identify security vulnerabilities
```

**You receive:**
```
Gemini scanned 47 files in ./src. Security vulnerabilities:

- SQL injection risk: api/database.py:45 (user input not sanitized)
- Hardcoded credentials: config/settings.py:12 (API key in source)
- Path traversal: files.py:89 (no validation on file uploads)
- Plaintext passwords: auth.py:78 (should use bcrypt)
- Missing CSRF protection: routes.py:34

I can help fix these issues. Which should we address first?
```

---

## Trigger Phrases

The skill auto-activates when you say:

**Direct Gemini requests:**
- "Use Gemini to analyze [file]"
- "Let Gemini scan [directory]"
- "Ask Gemini about [content]"
- "Gemini help me [task]"

**Implicit multimodal requests:**
- "Analyze this image/screenshot/photo"
- "Summarize this PDF/document"
- "Extract key points from this video"
- "Transcribe and summarize this audio"

**Codebase analysis:**
- "Scan the codebase for [issues]"
- "What does this project do?" (for large projects)
- "Identify [patterns/problems] across all files"

---

## Supported File Types

### Images
- PNG, JPG, JPEG, GIF, WebP
- Screenshots, diagrams, charts, photos

**Use cases:**
- UI/UX analysis
- Diagram explanation
- Chart/graph data extraction
- Screenshot debugging

### Documents
- PDF, DOCX, TXT, MD
- Research papers, reports, documentation

**Use cases:**
- Summarization
- Key point extraction
- Question answering
- Citation finding

### Audio
- MP3, WAV, M4A, OGG
- Meetings, podcasts, lectures

**Use cases:**
- Transcription
- Meeting minutes extraction
- Topic identification
- Speaker analysis

### Video
- MP4, MOV, AVI, WebM
- Tutorials, recordings, demos

**Use cases:**
- Content summarization
- Scene description
- Action extraction
- Tutorial step identification

### Code
- All text-based source files
- Entire directories with `--all-files`

**Use cases:**
- Security vulnerability scanning
- Architecture analysis
- Code quality review
- Pattern identification

---

## How It Works

### Architecture: Thin Skill + Thick Executor

**Gemini CLI Skill (Thin):**
- Recognizes Gemini-related requests
- Validates files exist
- Extracts user's prompt/question
- Dispatches to agent
- Returns summary to user

**General-Purpose Agent (Thick):**
- Constructs Gemini CLI command
- Executes command (isolated context)
- Processes potentially massive output
- Extracts 3-5 key findings
- Returns concise summary

### Context Isolation

**Without isolation (bad):**
```
User: Scan this codebase
Claude: [runs gemini, gets 5000 lines]
Main conversation: [now contains 5000 lines of Gemini output]
User: [next question gets poor response due to context pollution]
```

**With isolation (good):**
```
User: Scan this codebase
Skill: [dispatches agent]
Agent: [runs gemini, gets 5000 lines, extracts key points]
Agent → Skill: [summary: 5 bullets]
Skill → User: [clean summary]
Main conversation: [stays clean, 5 bullets only]
```

---

## Advanced Usage

### Custom Prompts

```bash
User: Use Gemini to analyze screenshot.png and specifically check for:
      - Accessibility issues (WCAG compliance)
      - Mobile responsiveness indicators
      - Visual design consistency
```

The skill extracts your detailed prompt and passes it to Gemini.

### Multiple Files

```bash
User: Let Gemini compare these two designs
      designs/v1.png designs/v2.png
```

Gemini analyzes both and identifies differences.

### Directory Scanning

```bash
User: Gemini scan ./src for performance bottlenecks
```

Uses `--all-files` to analyze entire directory.

### Follow-up Questions

```bash
User: Use Gemini to analyze report.pdf

Claude: [returns summary]

User: Ask Gemini for more detail on the methodology section
```

The skill can make multiple Gemini calls in same session.

---

## Best Practices

### 1. Be Specific in Requests

**Vague:**
```
User: Analyze this image
```

**Better:**
```
User: Use Gemini to analyze this image and identify UI/UX problems
```

**Best:**
```
User: Use Gemini to analyze screenshot.png for:
      - Layout issues
      - Color contrast problems
      - Typography hierarchy
      - Mobile responsiveness
```

### 2. Use Gemini for Its Strengths

**Good use cases:**
- Multimodal content (images, audio, video)
- Ultra-long documents (100+ pages)
- Large codebases (100+ files)
- Pattern recognition across many files

**Bad use cases:**
- Simple code questions (use Claude directly)
- Short text analysis (Claude is faster)
- File modification (Gemini is read-only)
- Tasks requiring context persistence

### 3. Combine with Other Skills

**Gemini + Brainstorming:**
```
User: Use Gemini to analyze our competitor's UI (screenshot.png)

Claude: [Gemini summary of findings]

User: /superpowers:brainstorm Design our UI based on these insights
```

**Gemini + Code Review:**
```
User: Let Gemini scan ./src for security issues

Claude: [Gemini finds 5 vulnerabilities]

User: /superpowers:write-plan Create plan to fix these issues
```

**Gemini + TDD:**
```
User: Gemini analyze this API spec (spec.pdf)

Claude: [Gemini extracts requirements]

User: Implement this API using codex-subagent-driven-development
```

### 4. Verify Sensitive Data

```bash
User: Scan config/ for issues

Claude: Warning: config/ may contain API keys or credentials.
        Sending to Gemini's external API will expose this data.
        Proceed? [y/n]
```

Always confirm before sending sensitive files.

---

## Comparison: Gemini vs Claude vs Codex

| Task | Best Tool | Why |
|------|-----------|-----|
| Analyze image | **Gemini** | Multimodal |
| Summarize 200-page PDF | **Gemini** | Ultra-long context |
| Scan 500 files for patterns | **Gemini** | Large codebase analysis |
| Write code | **Codex** | Code generation specialist |
| Review code | **Claude** | Context + reasoning |
| Edit existing file | **Claude** | Precise modifications |
| Answer coding question | **Claude** | Faster for short queries |
| Extract audio transcript | **Gemini** | Audio processing |

**Use all three together:**
1. **Gemini** analyzes requirements (from PDF/images)
2. **Claude** creates plan and writes tests
3. **Codex** implements code
4. **Claude** reviews and commits

---

## Troubleshooting

### Skill Doesn't Activate

**Symptom:** You say "use Gemini" but nothing happens.

**Causes:**
1. Skill not loaded
2. Phrase doesn't match triggers

**Fix:**
```bash
# Explicitly load skill
User: Load the gemini-cli skill

# Or use exact trigger phrase
User: Use Gemini to analyze [file]
```

### "gemini: command not found"

**Symptom:** Agent returns error about missing command.

**Fix:**
```bash
# Install Gemini CLI
[follow official installation instructions]

# Verify installation
gemini --version

# Ensure it's in PATH
which gemini
```

### Command Hangs

**Symptom:** Gemini command runs but never completes.

**Cause:** Missing `--yolo` flag (waiting for confirmation).

**Fix:** Agent should always include `--yolo`. If this happens, report as bug.

### Output Too Long

**Symptom:** You receive thousands of lines instead of summary.

**Cause:** Agent failed to extract key points.

**Fix:**
```bash
User: Please summarize the Gemini output to 5 key points
```

### File Not Found

**Symptom:** Error that file doesn't exist.

**Fixes:**
- Use absolute paths: `~/Documents/file.pdf`
- Verify file exists: `ls -la [path]`
- Check permissions: `ls -l [path]`

---

## Example Workflows

### Workflow 1: Competitive Analysis

```bash
# 1. Analyze competitor screenshots
User: Use Gemini to analyze these competitor UIs and identify patterns
      competitor1.png competitor2.png competitor3.png

# 2. Brainstorm based on insights
User: /superpowers:brainstorm Design our UI incorporating these insights

# 3. Implement
User: Create implementation plan and use codex-subagent-driven-development
```

### Workflow 2: Research Paper Implementation

```bash
# 1. Extract requirements from paper
User: Use Gemini to extract the algorithm description from paper.pdf

# 2. Plan implementation
User: /superpowers:write-plan Implement this algorithm in Python

# 3. Execute with TDD
User: Execute with codex-subagent-driven-development
```

### Workflow 3: Security Audit

```bash
# 1. Scan codebase
User: Let Gemini scan ./src for security vulnerabilities

# 2. Prioritize issues
User: Which of these issues is most critical?

# 3. Fix systematically
User: /superpowers:write-plan Fix the SQL injection issues

# 4. Verify fix
User: After fixes, let Gemini rescan to verify
```

---

## Cost Considerations

**Gemini Free Tier:**
- Daily quota (check with `gemini quota`)
- Sufficient for personal use
- May rate-limit on large files

**Cost optimization:**
- Use Gemini for multimodal/long-context only
- Use Claude for short text (faster, no quota)
- Batch similar requests
- Cache results when possible

---

## Limitations

**What Gemini Cannot Do:**
- Modify files (read-only analysis)
- Execute code
- Make API calls
- Persist context across sessions
- Real-time interaction

**What This Integration Cannot Do:**
- Bypass Gemini quota limits
- Process files larger than Gemini's limits
- Handle unsupported file types
- Work without Gemini CLI installed

---

## Next Steps

### Try It Yourself

**Simple test:**
```bash
User: Use Gemini to analyze this file and tell me what it does
      README.md
```

**Multimodal test (if you have image):**
```bash
User: Use Gemini to describe what's in this image
      [path-to-image]
```

### Extend the Integration

**Add custom agent:**
- Create `~/.claude/agents/gemini-executor.md`
- Customize prompt extraction
- Add domain-specific analysis

**Combine with workflows:**
- Gemini → Extract specs
- Brainstorm → Design
- Write Plan → Structure
- Codex → Implement
- Claude → Review

---

## Resources

**Files:**
- Skill: `skills/gemini-cli/SKILL.md`
- Agent: `agents/gemini-executor.md`
- This guide: `docs/gemini-cli-integration.md`

**Related:**
- Codex integration: `docs/quickstart-codex-subagent-workflow.md`
- Superpowers README: `README.md`
- Skills guide: `skills/writing-skills/SKILL.md`

**Get Help:**
- GitHub Issues: https://github.com/anna-belle-zhang/superpowerwithcodex/issues
- Original article: `geminicli.md`

---

**Ready to analyze multimodal content? Say "Use Gemini to analyze..."** 🚀
