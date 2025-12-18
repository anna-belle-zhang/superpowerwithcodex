import fs from 'fs/promises';
import path from 'path';
import { execSync, spawn } from 'child_process';
import readline from 'readline';

function commandExists(command) {
    try {
        if (process.platform === 'win32') {
            execSync(`where ${command}`, { stdio: 'ignore' });
        } else {
            execSync(`which ${command}`, { stdio: 'ignore' });
        }
        return true;
    } catch {
        return false;
    }
}

async function loadMCPConfig(options = {}) {
    const { cwd = process.cwd(), filename = '.mcp.json' } = options;
    const configPath = path.join(cwd, filename);

    try {
        const content = await fs.readFile(configPath, 'utf8');
        return JSON.parse(content);
    } catch {
        return null;
    }
}

async function testSpawn() {
    return { success: true };
}

function parseMcpTextResult(result) {
    if (!result) return '';

    if (typeof result === 'string') return result;

    if (typeof result?.output === 'string') return result.output;

    const content = result?.content;
    if (Array.isArray(content)) {
        const textParts = content
            .map((part) => (typeof part?.text === 'string' ? part.text : ''))
            .filter(Boolean);
        if (textParts.length > 0) return textParts.join('\n');
    }

    try {
        return JSON.stringify(result);
    } catch {
        return String(result);
    }
}

async function callMcpTool(serverSpec, options) {
    const { toolName, toolArgs, cwd, timeoutMs = 60000, onProgress } = options;
    if (!serverSpec?.command) throw new Error('MCP server config missing "command"');

    const child = spawn(serverSpec.command, serverSpec.args || [], {
        cwd: cwd || process.cwd(),
        stdio: ['pipe', 'pipe', 'pipe']
    });

    const rl = readline.createInterface({ input: child.stdout });
    const pending = new Map();

    const failAll = (error) => {
        for (const [, { reject }] of pending.entries()) reject(error);
        pending.clear();
    };

    child.on('error', (err) => failAll(err));
    child.stderr.on('data', (buf) => {
        if (onProgress) onProgress(buf.toString('utf8'));
    });

    rl.on('line', (line) => {
        const trimmed = line.trim();
        if (!trimmed) return;

        let message;
        try {
            message = JSON.parse(trimmed);
        } catch {
            return;
        }

        if (message?.id && pending.has(message.id)) {
            const { resolve, reject } = pending.get(message.id);
            pending.delete(message.id);
            if (message.error) reject(new Error(message.error?.message || 'MCP error'));
            else resolve(message.result);
            return;
        }

        if (onProgress && message?.method) {
            try {
                onProgress(`[mcp] ${message.method}`);
            } catch {
                // ignore progress callback failures
            }
        }
    });

    const send = (payload) => {
        child.stdin.write(`${JSON.stringify(payload)}\n`);
    };

    const request = (payload) =>
        new Promise((resolve, reject) => {
            pending.set(payload.id, { resolve, reject });
            send(payload);
        });

    const withTimeout = async (promise) => {
        let timeout;
        const timeoutPromise = new Promise((_, reject) => {
            timeout = setTimeout(() => reject(new Error('MCP timeout')), timeoutMs);
        });

        try {
            return await Promise.race([promise, timeoutPromise]);
        } finally {
            clearTimeout(timeout);
        }
    };

    try {
        await withTimeout(
            request({
                jsonrpc: '2.0',
                id: 1,
                method: 'initialize',
                params: {
                    protocolVersion: '2024-11-05',
                    capabilities: {},
                    clientInfo: { name: 'superpowers-codex-integration', version: '0.1.0' }
                }
            })
        );

        send({ jsonrpc: '2.0', method: 'initialized', params: {} });

        const result = await withTimeout(
            request({
                jsonrpc: '2.0',
                id: 2,
                method: 'tools/call',
                params: { name: toolName, arguments: toolArgs || {} }
            })
        );

        return result;
    } finally {
        rl.close();
        child.kill();
    }
}

/**
 * Check if Codex is available and properly configured.
 *
 * Checks:
 * - `.mcp.json` exists and contains `mcpServers.codex-subagent`
 * - `codex` CLI is on PATH
 *
 * @returns {Promise<{available: boolean, error?: string}>}
 */
async function checkCodexAvailability() {
    try {
        const mcpConfig = await loadMCPConfig();
        if (!mcpConfig) {
            return { available: false, error: 'MCP config file .mcp.json not found' };
        }

        if (!mcpConfig?.mcpServers?.['codex-subagent']) {
            return { available: false, error: 'codex-subagent not configured in .mcp.json' };
        }

        if (!commandExists('codex')) {
            return { available: false, error: 'codex CLI not found on PATH' };
        }

        const spawnResult = await testSpawn();
        if (!spawnResult.success) {
            return { available: false, error: spawnResult.error || 'Codex spawn test failed' };
        }

        return { available: true };
    } catch (error) {
        return { available: false, error: error?.message || 'Unknown error' };
    }
}

/**
 * Execute a task with Codex via MCP.
 *
 * Note: this is currently a scaffold. It validates retries and reporting,
 * but does not yet perform real MCP protocol calls.
 *
 * @param {Object} config
 * @param {string} config.prompt
 * @param {string} config.workingDir
 * @param {number} config.retryCount
 * @param {(message: string) => void} [config.onProgress]
 * @returns {Promise<{success: boolean, output?: string, error?: string, attempts: number}>}
 */
async function executeWithCodex(config) {
    const { prompt, workingDir, retryCount = 0, onProgress } = config || {};

    if (!prompt || typeof prompt !== 'string') {
        return { success: false, error: 'config.prompt must be a non-empty string', attempts: 0 };
    }

    let attempts = 0;
    let lastError = null;

    while (attempts <= retryCount) {
        attempts += 1;

        if (onProgress) {
            onProgress(`Codex implementing... (attempt ${attempts}/${retryCount + 1})`);
        }

        try {
            const result = await spawnCodexAgent(prompt, workingDir);
            if (result.success) {
                if (onProgress) onProgress('Codex completed successfully');
                return { success: true, output: result.output, attempts };
            }

            lastError = result.error || 'Codex execution failed';
        } catch (error) {
            lastError = error?.message || 'Codex execution failed';
        }
    }

    return { success: false, error: lastError || 'Codex execution failed', attempts };
}

async function spawnCodexAgent(prompt, workingDir) {
    // Load MCP config from project root (where superpowers is installed)
    // but execute Codex in the specified workingDir
    const mcpConfig = await loadMCPConfig({ cwd: process.cwd() });
    if (!mcpConfig?.mcpServers?.['codex-subagent']) {
        return { success: false, error: 'codex-subagent not configured in .mcp.json' };
    }

    const serverSpec = mcpConfig.mcpServers['codex-subagent'];
    try {
        const result = await callMcpTool(serverSpec, {
            toolName: 'spawn_agent',
            toolArgs: { prompt },
            cwd: workingDir || process.cwd()
        });

        const output = parseMcpTextResult(result);
        if (output.startsWith('Error:')) {
            return { success: false, error: output };
        }

        return { success: true, output };
    } catch (error) {
        return { success: false, error: error?.message || 'MCP tool call failed' };
    }
}

/**
 * Format retry prompt with feedback and research guidance.
 *
 * @param {string} originalPrompt
 * @param {Object} feedback
 * @param {number} attempt 1-based attempt number
 * @param {number} maxRetries retry count
 * @returns {Promise<{prompt: string, shouldEscalate: boolean}>}
 */
async function retryWithFeedback(originalPrompt, feedback, attempt, maxRetries) {
    if (attempt > maxRetries) {
        return { prompt: '', shouldEscalate: true };
    }

    let retryPrompt = `RETRY ATTEMPT ${attempt} of ${maxRetries}\n\n`;
    retryPrompt += `Original Task:\n${originalPrompt}\n\n`;
    retryPrompt += `Previous Attempt Failed:\n`;

    if (feedback?.failure_type === 'test_failure') {
        retryPrompt += `Test Output:\n${feedback.test_output || ''}\n\n`;
    } else if (feedback?.failure_type === 'review_issues') {
        retryPrompt += `Review Issues:\n${feedback.review_issues || ''}\n\n`;
    } else {
        retryPrompt += `${JSON.stringify(feedback || {}, null, 2)}\n\n`;
    }

    if (attempt === 2) {
        retryPrompt += `IMPORTANT - Research Required:\n`;
        retryPrompt += `Before implementing, research:\n`;
        retryPrompt += `- Latest API documentation and parameter signatures\n`;
        retryPrompt += `- Recent breaking changes or deprecations\n`;
        retryPrompt += `- Updated official examples\n`;
        retryPrompt += `- Version compatibility issues\n\n`;
    }

    retryPrompt += `Please fix the issues and try again.\n`;
    if (attempt === maxRetries) {
        retryPrompt += `This is your FINAL attempt.\n`;
    }

    return { prompt: retryPrompt, shouldEscalate: false };
}

/**
 * Detect file boundary violations.
 *
 * Rules:
 * - Any file in `read_only` is a violation.
 * - If `implement_in` is non-empty, any changed file outside `implement_in` is a violation.
 *
 * @param {string[]} changedFiles
 * @param {Object} boundaries
 * @param {string[]} [boundaries.implement_in]
 * @param {string[]} [boundaries.read_only]
 * @returns {Promise<string[]>}
 */
async function detectBoundaryViolations(changedFiles, boundaries) {
    const implementIn = boundaries?.implement_in || [];
    const readOnly = boundaries?.read_only || [];
    const changed = Array.isArray(changedFiles) ? changedFiles : [];

    const violations = new Set();

    for (const file of changed) {
        if (readOnly.includes(file)) violations.add(file);
        if (implementIn.length > 0 && !implementIn.includes(file)) violations.add(file);
    }

    return [...violations];
}

function buildFileBoundaries(task) {
    return {
        implement_in: task?.implementIn || [],
        read_only: task?.readOnly || [],
        tests_to_pass: task?.testsToPass || []
    };
}

function formatBoundaryInstructions(boundaries) {
    const implementIn = boundaries?.implement_in || [];
    const readOnly = boundaries?.read_only || [];

    let instructions = '';

    if (implementIn.length > 0) {
        instructions += `Implement in ONLY these files:\n`;
        for (const file of implementIn) instructions += `- ${file}\n`;
        instructions += `\n`;
    }

    if (readOnly.length > 0) {
        instructions += `DO NOT MODIFY these files:\n`;
        for (const file of readOnly) instructions += `- ${file} (READ ONLY)\n`;
        instructions += `\n`;
    }

    instructions += `You may READ any file to understand context.\n`;
    instructions += `You must ONLY WRITE to the "Implement in" files listed above.\n`;

    return instructions;
}

export {
    checkCodexAvailability,
    executeWithCodex,
    retryWithFeedback,
    detectBoundaryViolations,
    buildFileBoundaries,
    formatBoundaryInstructions
};
