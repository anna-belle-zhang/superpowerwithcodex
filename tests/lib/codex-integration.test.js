import { jest } from '@jest/globals';
import fs from 'fs/promises';
import path from 'path';

// Mock fs module
jest.unstable_mockModule('fs/promises', () => ({
    access: jest.fn(),
    readFile: jest.fn()
}));

// Import after mocking
const { detectE2EStrategy } = await import('../../lib/codex-integration.js');
const mockFs = await import('fs/promises');

describe('detectE2EStrategy', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    describe('Playwright detection', () => {
        test('detects playwright.config.ts', async () => {
            mockFs.access.mockImplementation(async (filepath) => {
                if (filepath.endsWith('playwright.config.ts')) return;
                throw new Error('ENOENT');
            });
            mockFs.readFile.mockRejectedValue(new Error('ENOENT'));

            const result = await detectE2EStrategy('/test/project');

            expect(result.type).toBe('playwright');
            expect(result.command).toBe('npx playwright test');
        });

        test('detects playwright.config.js', async () => {
            mockFs.access.mockImplementation(async (filepath) => {
                if (filepath.endsWith('playwright.config.js')) return;
                throw new Error('ENOENT');
            });
            mockFs.readFile.mockRejectedValue(new Error('ENOENT'));

            const result = await detectE2EStrategy('/test/project');

            expect(result.type).toBe('playwright');
        });
    });

    describe('Cypress detection', () => {
        test('detects cypress.config.ts', async () => {
            mockFs.access.mockImplementation(async (filepath) => {
                if (filepath.endsWith('cypress.config.ts')) return;
                throw new Error('ENOENT');
            });
            mockFs.readFile.mockRejectedValue(new Error('ENOENT'));

            const result = await detectE2EStrategy('/test/project');

            expect(result.type).toBe('cypress');
            expect(result.command).toBe('npx cypress run');
        });
    });

    describe('Web framework detection', () => {
        test('detects React project', async () => {
            mockFs.access.mockRejectedValue(new Error('ENOENT'));
            mockFs.readFile.mockResolvedValue(JSON.stringify({
                dependencies: { react: '^18.0.0' }
            }));

            const result = await detectE2EStrategy('/test/project');

            expect(result.type).toBe('playwright');
            expect(result.description).toContain('web framework detected');
        });

        test('detects Vue project', async () => {
            mockFs.access.mockRejectedValue(new Error('ENOENT'));
            mockFs.readFile.mockResolvedValue(JSON.stringify({
                dependencies: { vue: '^3.0.0' }
            }));

            const result = await detectE2EStrategy('/test/project');

            expect(result.type).toBe('playwright');
        });

        test('detects Next.js project', async () => {
            mockFs.access.mockRejectedValue(new Error('ENOENT'));
            mockFs.readFile.mockResolvedValue(JSON.stringify({
                dependencies: { next: '^14.0.0' }
            }));

            const result = await detectE2EStrategy('/test/project');

            expect(result.type).toBe('playwright');
        });
    });

    describe('CLI detection', () => {
        test('detects CLI project with bin field', async () => {
            mockFs.access.mockRejectedValue(new Error('ENOENT'));
            mockFs.readFile.mockResolvedValue(JSON.stringify({
                bin: { mycli: './bin/cli.js' }
            }));

            const result = await detectE2EStrategy('/test/project');

            expect(result.type).toBe('cli');
            expect(result.description).toContain('CLI');
        });
    });

    describe('API detection', () => {
        test('detects OpenAPI spec (yaml)', async () => {
            mockFs.access.mockImplementation(async (filepath) => {
                if (filepath.endsWith('openapi.yaml')) return;
                throw new Error('ENOENT');
            });
            mockFs.readFile.mockRejectedValue(new Error('ENOENT'));

            const result = await detectE2EStrategy('/test/project');

            expect(result.type).toBe('api');
            expect(result.description).toContain('API');
        });

        test('detects Swagger spec', async () => {
            mockFs.access.mockImplementation(async (filepath) => {
                if (filepath.endsWith('swagger.json')) return;
                throw new Error('ENOENT');
            });
            mockFs.readFile.mockRejectedValue(new Error('ENOENT'));

            const result = await detectE2EStrategy('/test/project');

            expect(result.type).toBe('api');
        });
    });

    describe('Default fallback', () => {
        test('falls back to bash when no config detected', async () => {
            mockFs.access.mockRejectedValue(new Error('ENOENT'));
            mockFs.readFile.mockRejectedValue(new Error('ENOENT'));

            const result = await detectE2EStrategy('/test/project');

            expect(result.type).toBe('bash');
            expect(result.command).toContain('npm run test:e2e');
        });
    });

    describe('Priority order', () => {
        test('Playwright config takes priority over package.json framework', async () => {
            mockFs.access.mockImplementation(async (filepath) => {
                if (filepath.endsWith('playwright.config.ts')) return;
                throw new Error('ENOENT');
            });
            mockFs.readFile.mockResolvedValue(JSON.stringify({
                dependencies: { react: '^18.0.0' }
            }));

            const result = await detectE2EStrategy('/test/project');

            // Should detect Playwright config, not React
            expect(result.type).toBe('playwright');
            expect(result.description).not.toContain('web framework');
        });
    });
});
