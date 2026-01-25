import { execSync } from 'child_process';
import {
    checkCodexAvailability,
    executeWithCodex,
    retryWithFeedback,
    detectE2EStrategy,
    runE2ETests
} from './codex-integration.js';

/**
 * Ralph-Codex-E2E Orchestrator
 *
 * Coordinates the workflow:
 * 1. Codex: implementation + unit tests + integration tests
 * 2. Claude: E2E tests (project-specific)
 * 3. Loop until all tests pass
 */

/**
 * Run tests with a specified command.
 *
 * @param {string} command - Test command to run
 * @param {string} [cwd] - Working directory
 * @returns {{success: boolean, output: string}}
 */
function runTests(command, cwd = process.cwd()) {
    try {
        const output = execSync(command, {
            cwd,
            encoding: 'utf8',
            stdio: ['pipe', 'pipe', 'pipe'],
            timeout: 300000 // 5 minute timeout
        });
        return { success: true, output };
    } catch (error) {
        const output = error.stdout || error.stderr || error.message || 'Tests failed';
        return { success: false, output };
    }
}

/**
 * Retry chain configuration.
 */
const RETRY_CONFIG = {
    codexMaxRetries: 2,
    claudeMaxRetries: 2
};

/**
 * Execute a single task with the Codex phase.
 *
 * Steps:
 * 1. Dispatch Codex to implement + write unit/integration tests
 * 2. Run unit tests
 * 3. Run integration tests
 * 4. Retry if failures (up to max retries)
 *
 * @param {Object} task - Task configuration
 * @param {string} task.prompt - Task prompt for Codex
 * @param {string} task.unitTestCommand - Command to run unit tests
 * @param {string} task.integrationTestCommand - Command to run integration tests
 * @param {string} [task.workingDir] - Working directory
 * @param {(message: string) => void} [onProgress] - Progress callback
 * @returns {Promise<{success: boolean, phase: string, output: string, attempts: number}>}
 */
async function executeCodexPhase(task, onProgress) {
    const { prompt, unitTestCommand, integrationTestCommand, workingDir } = task;
    let attempts = 0;
    let lastOutput = '';

    // Check Codex availability
    const availability = await checkCodexAvailability();
    if (!availability.available) {
        return {
            success: false,
            phase: 'codex_availability',
            output: `Codex not available: ${availability.error}`,
            attempts: 0
        };
    }

    while (attempts < RETRY_CONFIG.codexMaxRetries) {
        attempts++;
        if (onProgress) onProgress(`Codex phase attempt ${attempts}/${RETRY_CONFIG.codexMaxRetries}`);

        // Execute Codex
        const codexResult = await executeWithCodex({
            prompt,
            workingDir,
            retryCount: 0, // We handle retries at this level
            onProgress
        });

        if (!codexResult.success) {
            lastOutput = codexResult.error || 'Codex execution failed';
            if (onProgress) onProgress(`Codex failed: ${lastOutput}`);
            continue;
        }

        // Run unit tests
        if (unitTestCommand) {
            if (onProgress) onProgress('Running unit tests...');
            const unitResult = runTests(unitTestCommand, workingDir);

            if (!unitResult.success) {
                lastOutput = unitResult.output;
                if (onProgress) onProgress(`Unit tests failed: ${lastOutput.slice(0, 200)}`);

                // Prepare retry with feedback
                const { prompt: retryPrompt } = await retryWithFeedback(
                    prompt,
                    { failure_type: 'test_failure', test_output: unitResult.output },
                    attempts,
                    RETRY_CONFIG.codexMaxRetries
                );

                if (attempts < RETRY_CONFIG.codexMaxRetries) {
                    task.prompt = retryPrompt;
                }
                continue;
            }
            if (onProgress) onProgress('Unit tests passed');
        }

        // Run integration tests
        if (integrationTestCommand) {
            if (onProgress) onProgress('Running integration tests...');
            const integResult = runTests(integrationTestCommand, workingDir);

            if (!integResult.success) {
                lastOutput = integResult.output;
                if (onProgress) onProgress(`Integration tests failed: ${lastOutput.slice(0, 200)}`);

                // Prepare retry with feedback
                const { prompt: retryPrompt } = await retryWithFeedback(
                    prompt,
                    { failure_type: 'test_failure', test_output: integResult.output },
                    attempts,
                    RETRY_CONFIG.codexMaxRetries
                );

                if (attempts < RETRY_CONFIG.codexMaxRetries) {
                    task.prompt = retryPrompt;
                }
                continue;
            }
            if (onProgress) onProgress('Integration tests passed');
        }

        // All tests passed
        return {
            success: true,
            phase: 'codex',
            output: codexResult.output || 'Codex phase completed successfully',
            attempts
        };
    }

    // Codex retries exhausted
    return {
        success: false,
        phase: 'codex_exhausted',
        output: lastOutput,
        attempts
    };
}

/**
 * Execute the Claude E2E phase.
 *
 * @param {Object} options
 * @param {string} [options.projectRoot] - Project root directory
 * @param {string} [options.customCommand] - Override E2E command
 * @param {(message: string) => void} [options.onProgress] - Progress callback
 * @returns {Promise<{success: boolean, phase: string, output: string, strategy: Object, attempts: number}>}
 */
async function executeClaudeE2EPhase(options = {}) {
    const { projectRoot, customCommand, onProgress } = options;
    let attempts = 0;

    // Detect E2E strategy
    const strategy = await detectE2EStrategy(projectRoot);
    if (onProgress) onProgress(`E2E strategy detected: ${strategy.type} - ${strategy.description}`);

    while (attempts < RETRY_CONFIG.claudeMaxRetries) {
        attempts++;
        if (onProgress) onProgress(`Claude E2E phase attempt ${attempts}/${RETRY_CONFIG.claudeMaxRetries}`);

        const result = await runE2ETests({
            projectRoot,
            customCommand,
            onProgress
        });

        if (result.success) {
            return {
                success: true,
                phase: 'e2e',
                output: result.output,
                strategy: result.strategy,
                attempts
            };
        }

        if (onProgress) onProgress(`E2E attempt ${attempts} failed, retrying...`);
    }

    // E2E retries exhausted - this signals Ralph to loop
    const finalResult = await runE2ETests({ projectRoot, customCommand });
    return {
        success: false,
        phase: 'e2e_exhausted',
        output: finalResult.output,
        strategy: finalResult.strategy,
        attempts
    };
}

/**
 * Execute a full task cycle: Codex phase → Claude E2E phase.
 *
 * @param {Object} task - Task configuration
 * @param {string} task.prompt - Task prompt for Codex
 * @param {string} [task.unitTestCommand] - Unit test command
 * @param {string} [task.integrationTestCommand] - Integration test command
 * @param {string} [task.e2eCommand] - Custom E2E command
 * @param {string} [task.workingDir] - Working directory
 * @param {(message: string) => void} [onProgress] - Progress callback
 * @returns {Promise<{success: boolean, codexResult: Object, e2eResult: Object}>}
 */
async function executeTaskCycle(task, onProgress) {
    const { workingDir, e2eCommand } = task;

    if (onProgress) onProgress('=== Starting task cycle ===');

    // Phase 1: Codex
    if (onProgress) onProgress('--- Codex Phase ---');
    const codexResult = await executeCodexPhase(task, onProgress);

    if (!codexResult.success) {
        // Codex failed after retries - try Claude fix
        if (onProgress) onProgress('Codex exhausted, Claude fix not implemented yet');
        return {
            success: false,
            codexResult,
            e2eResult: null
        };
    }

    // Phase 2: Claude E2E
    if (onProgress) onProgress('--- Claude E2E Phase ---');
    const e2eResult = await executeClaudeE2EPhase({
        projectRoot: workingDir,
        customCommand: e2eCommand,
        onProgress
    });

    const success = codexResult.success && e2eResult.success;
    if (onProgress) {
        onProgress(success ? '=== Task cycle PASSED ===' : '=== Task cycle FAILED ===');
    }

    return {
        success,
        codexResult,
        e2eResult
    };
}

/**
 * Check if all tests pass (completion condition for Ralph loop).
 *
 * @param {Object} options
 * @param {string} [options.unitTestCommand]
 * @param {string} [options.integrationTestCommand]
 * @param {string} [options.projectRoot]
 * @param {(message: string) => void} [options.onProgress]
 * @returns {Promise<{allGreen: boolean, results: Object}>}
 */
async function checkAllTestsGreen(options = {}) {
    const { unitTestCommand, integrationTestCommand, projectRoot, onProgress } = options;

    const results = {
        unit: null,
        integration: null,
        e2e: null
    };

    // Unit tests
    if (unitTestCommand) {
        if (onProgress) onProgress('Checking unit tests...');
        results.unit = runTests(unitTestCommand, projectRoot);
    }

    // Integration tests
    if (integrationTestCommand) {
        if (onProgress) onProgress('Checking integration tests...');
        results.integration = runTests(integrationTestCommand, projectRoot);
    }

    // E2E tests
    if (onProgress) onProgress('Checking E2E tests...');
    results.e2e = await runE2ETests({ projectRoot, onProgress });

    const allGreen =
        (results.unit === null || results.unit.success) &&
        (results.integration === null || results.integration.success) &&
        results.e2e.success;

    if (onProgress) {
        onProgress(allGreen ? 'All tests GREEN' : 'Some tests FAILED');
    }

    return { allGreen, results };
}

export {
    executeCodexPhase,
    executeClaudeE2EPhase,
    executeTaskCycle,
    checkAllTestsGreen,
    runTests,
    RETRY_CONFIG
};
