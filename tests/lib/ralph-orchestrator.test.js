import { jest } from '@jest/globals';

// Mock child_process
jest.unstable_mockModule('child_process', () => ({
    execSync: jest.fn()
}));

// Mock codex-integration
jest.unstable_mockModule('../../lib/codex-integration.js', () => ({
    checkCodexAvailability: jest.fn(),
    executeWithCodex: jest.fn(),
    retryWithFeedback: jest.fn(),
    detectE2EStrategy: jest.fn(),
    runE2ETests: jest.fn()
}));

// Import after mocking
const { execSync } = await import('child_process');
const codexIntegration = await import('../../lib/codex-integration.js');
const {
    executeCodexPhase,
    executeClaudeE2EPhase,
    executeTaskCycle,
    checkAllTestsGreen,
    runTests,
    RETRY_CONFIG
} = await import('../../lib/ralph-orchestrator.js');

describe('ralph-orchestrator', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    describe('RETRY_CONFIG', () => {
        test('has correct default values', () => {
            expect(RETRY_CONFIG.codexMaxRetries).toBe(2);
            expect(RETRY_CONFIG.claudeMaxRetries).toBe(2);
        });
    });

    describe('runTests', () => {
        test('returns success when command passes', () => {
            execSync.mockReturnValue('All tests passed');

            const result = runTests('npm test');

            expect(result.success).toBe(true);
            expect(result.output).toBe('All tests passed');
        });

        test('returns failure when command throws', () => {
            const error = new Error('Test failed');
            error.stdout = 'FAIL: test.js';
            execSync.mockImplementation(() => {
                throw error;
            });

            const result = runTests('npm test');

            expect(result.success).toBe(false);
            expect(result.output).toBe('FAIL: test.js');
        });
    });

    describe('executeCodexPhase', () => {
        test('returns error when Codex not available', async () => {
            codexIntegration.checkCodexAvailability.mockResolvedValue({
                available: false,
                error: 'Codex not installed'
            });

            const result = await executeCodexPhase({
                prompt: 'test prompt',
                unitTestCommand: 'npm test'
            });

            expect(result.success).toBe(false);
            expect(result.phase).toBe('codex_availability');
            expect(result.output).toContain('Codex not available');
        });

        test('succeeds when Codex and tests pass', async () => {
            codexIntegration.checkCodexAvailability.mockResolvedValue({ available: true });
            codexIntegration.executeWithCodex.mockResolvedValue({
                success: true,
                output: 'Implementation complete'
            });
            execSync.mockReturnValue('Tests passed');

            const result = await executeCodexPhase({
                prompt: 'test prompt',
                unitTestCommand: 'npm run test:unit',
                integrationTestCommand: 'npm run test:integration'
            });

            expect(result.success).toBe(true);
            expect(result.phase).toBe('codex');
        });

        test('retries when unit tests fail', async () => {
            codexIntegration.checkCodexAvailability.mockResolvedValue({ available: true });
            codexIntegration.executeWithCodex.mockResolvedValue({ success: true, output: 'Done' });
            codexIntegration.retryWithFeedback.mockResolvedValue({ prompt: 'retry prompt' });

            // First call fails, second succeeds
            let callCount = 0;
            execSync.mockImplementation(() => {
                callCount++;
                if (callCount === 1) {
                    const error = new Error('Test failed');
                    error.stdout = 'FAIL';
                    throw error;
                }
                return 'PASS';
            });

            const result = await executeCodexPhase({
                prompt: 'test prompt',
                unitTestCommand: 'npm test'
            });

            expect(result.success).toBe(true);
            expect(result.attempts).toBe(2);
        });
    });

    describe('executeClaudeE2EPhase', () => {
        test('succeeds when E2E tests pass', async () => {
            codexIntegration.detectE2EStrategy.mockResolvedValue({
                type: 'playwright',
                command: 'npx playwright test',
                description: 'Browser E2E'
            });
            codexIntegration.runE2ETests.mockResolvedValue({
                success: true,
                output: 'E2E passed',
                strategy: { type: 'playwright' }
            });

            const result = await executeClaudeE2EPhase({ projectRoot: '/test' });

            expect(result.success).toBe(true);
            expect(result.phase).toBe('e2e');
        });

        test('retries on E2E failure', async () => {
            codexIntegration.detectE2EStrategy.mockResolvedValue({
                type: 'bash',
                command: 'npm run test:e2e',
                description: 'System E2E'
            });

            // First fails, second succeeds
            let callCount = 0;
            codexIntegration.runE2ETests.mockImplementation(async () => {
                callCount++;
                if (callCount === 1) {
                    return { success: false, output: 'E2E failed', strategy: { type: 'bash' } };
                }
                return { success: true, output: 'E2E passed', strategy: { type: 'bash' } };
            });

            const result = await executeClaudeE2EPhase({ projectRoot: '/test' });

            expect(result.success).toBe(true);
            expect(result.attempts).toBe(2);
        });
    });

    describe('executeTaskCycle', () => {
        test('runs both Codex and E2E phases', async () => {
            codexIntegration.checkCodexAvailability.mockResolvedValue({ available: true });
            codexIntegration.executeWithCodex.mockResolvedValue({ success: true, output: 'Done' });
            codexIntegration.detectE2EStrategy.mockResolvedValue({
                type: 'bash',
                command: 'npm run test:e2e',
                description: 'System E2E'
            });
            codexIntegration.runE2ETests.mockResolvedValue({
                success: true,
                output: 'E2E passed',
                strategy: { type: 'bash' }
            });
            execSync.mockReturnValue('Tests passed');

            const result = await executeTaskCycle({
                prompt: 'implement feature',
                unitTestCommand: 'npm test'
            });

            expect(result.success).toBe(true);
            expect(result.codexResult.success).toBe(true);
            expect(result.e2eResult.success).toBe(true);
        });

        test('stops if Codex phase fails', async () => {
            codexIntegration.checkCodexAvailability.mockResolvedValue({
                available: false,
                error: 'Not configured'
            });

            const result = await executeTaskCycle({
                prompt: 'implement feature'
            });

            expect(result.success).toBe(false);
            expect(result.codexResult.success).toBe(false);
            expect(result.e2eResult).toBeNull();
        });
    });

    describe('checkAllTestsGreen', () => {
        test('returns true when all tests pass', async () => {
            execSync.mockReturnValue('Tests passed');
            codexIntegration.runE2ETests.mockResolvedValue({
                success: true,
                output: 'E2E passed'
            });

            const result = await checkAllTestsGreen({
                unitTestCommand: 'npm run test:unit',
                integrationTestCommand: 'npm run test:integration'
            });

            expect(result.allGreen).toBe(true);
        });

        test('returns false when any test fails', async () => {
            execSync.mockReturnValue('Tests passed');
            codexIntegration.runE2ETests.mockResolvedValue({
                success: false,
                output: 'E2E failed'
            });

            const result = await checkAllTestsGreen({
                unitTestCommand: 'npm run test:unit'
            });

            expect(result.allGreen).toBe(false);
        });

        test('skips tests when command not provided', async () => {
            codexIntegration.runE2ETests.mockResolvedValue({
                success: true,
                output: 'E2E passed'
            });

            const result = await checkAllTestsGreen({});

            expect(result.allGreen).toBe(true);
            expect(result.results.unit).toBeNull();
            expect(result.results.integration).toBeNull();
        });
    });
});
