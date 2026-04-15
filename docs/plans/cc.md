To enable Codex to call Claude Code (CC) in a reciprocal fashion, you can indeed create a claudecode-companion.mjs wrapper. This reverses the existing orchestration, allowing you to trigger CC from within a Codex session to bypass "brainstorming" or perform specialized architectural checks.1. How to Build claudecode-companion.mjsTo work effectively, this script must use Claude Code's headless mode (also known as the Agent SDK) to execute non-interactively.Core script logic:javascript// claudecode-companion.mjs (Simplified concept)
import { spawn } from 'child_process';

const task = process.argv.slice(2).join(' ');
// Use the -p (print) flag for non-interactive execution
const claude = spawn('claude', [
  '-p', task, 
  '--allowedTools', 'all', // Auto-approves file edits to prevent stuck sessions
  '--output-format', 'json'
]);

claude.stdout.on('data', (data) => console.log(data.toString()));
Use code with caution.2. Why this solves "Brainstorming" DegradationWhen CC slips into brainstorming mode, it's often due to open-ended conversational context. By calling it through a companion script with strict flags, you force a different behaviour:Targeted Execution: You can pass the task as a direct command (e.g., claude -p "Implement the feature defined in spec.md") which restricts its ability to deviate into text-heavy chatter.Permission Bypassing: Using --allowedTools all (or the alias claude dangerously skip permissions) removes the interactive "Yes/No" prompts that frequently cause CC to stall or "compact" its memory prematurely.3. Comparison of Companion RolesDirectionToolPurposeCC → Codexcodex-companion.mjsUses /codex:rescue to finish tasks where Claude is stuck in a loop.Codex → CCclaudecode-companion.mjsUses claude -p to get high-reasoning "Staff Engineer" reviews or architectural audits.4. Integration with superpowerwithcodexYou can register this new companion as a Codex "Executor" by adding it to your ~/.codex/config.toml:toml[executors.claude]
command = "node /path/to/claudecode-companion.mjs"
Use code with caution.This allows you to run commands like $.claude "Check this logic for regressions" directly from your Codex workflow.