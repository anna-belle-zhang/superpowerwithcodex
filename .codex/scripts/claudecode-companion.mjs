#!/usr/bin/env node

import { spawn } from "node:child_process";
import fs from "node:fs";
import process from "node:process";

import { parseArgs, splitRawArgumentString } from "./lib/args.mjs";
import { ensureAbsolutePath, readStdinIfPiped } from "./lib/fs.mjs";
import { binaryAvailable } from "./lib/process.mjs";

const DEFAULT_MODEL = "claude-sonnet-4-6";
const DEFAULT_MAX_TURNS = 10;
const READ_ONLY_TOOLS = "Read,Glob,Grep,WebFetch,WebSearch";
const WRITE_TOOLS = "Read,Glob,Grep,Edit,Write,Bash,WebFetch,WebSearch";

export function printUsage() {
  process.stdout.write(
    [
      "Usage:",
      "  node scripts/claudecode-companion.mjs task [--write] [--json] [--prompt-file <path>] [--cwd <path>] [--model <model>] [--max-turns <n>] [prompt]",
      "",
      "Subcommands:",
      "  task    Run Claude Code in headless stream-json mode for a single prompt.",
      "",
      "Flags:",
      "  --write              Allow Edit, Write, and Bash tools.",
      "  --json               Emit one JSON envelope when the run finishes.",
      "  --prompt-file <path> Read the prompt from a file.",
      "  --cwd <path>         Run Claude in the given working directory.",
      "  --model <model>      Override the default model.",
      "  --max-turns <n>      Override the default max turn count (10).",
      "  --help               Show this help text."
    ].join("\n") + "\n"
  );
}

export function normalizeArgv(argv) {
  if (argv.length === 1) {
    const [raw] = argv;
    if (!raw || !raw.trim()) {
      return [];
    }
    return splitRawArgumentString(raw);
  }
  return argv;
}

export function parseCommandInput(argv) {
  return parseArgs(normalizeArgv(argv), {
    valueOptions: ["prompt-file", "cwd", "model", "max-turns"],
    booleanOptions: ["help", "json", "write"],
    aliasMap: {
      C: "cwd"
    }
  });
}

export function buildAllowedTools(writeEnabled) {
  return writeEnabled ? WRITE_TOOLS : READ_ONLY_TOOLS;
}

export function buildClaudeLaunch(platform = process.platform) {
  if (platform === "win32") {
    return { command: "claude.cmd", shell: true };
  }
  return { command: "claude", shell: false };
}

function resolvePrompt(positionals, options, cwd, readStdinIfPipedImpl) {
  if (options["prompt-file"]) {
    const promptPath = ensureAbsolutePath(cwd, options["prompt-file"]);
    return fs.readFileSync(promptPath, "utf8");
  }

  if (positionals.length > 0) {
    return positionals.join(" ");
  }

  return readStdinIfPipedImpl();
}

function parseMaxTurns(rawValue) {
  if (rawValue == null) {
    return DEFAULT_MAX_TURNS;
  }
  const parsed = Number.parseInt(String(rawValue), 10);
  if (!Number.isInteger(parsed) || parsed < 1) {
    throw new Error("--max-turns must be a positive integer.");
  }
  return parsed;
}

function flushJsonLines(buffer, onEvent, stderr) {
  const lines = buffer.split(/\r?\n/);
  const remainder = lines.pop() ?? "";

  for (const line of lines) {
    if (!line.trim()) {
      continue;
    }

    try {
      onEvent(JSON.parse(line));
    } catch (error) {
      stderr.write(`Failed to parse Claude stream-json output: ${error.message}\n`);
    }
  }

  return remainder;
}

export function runTaskCommand(argv, io = {}) {
  const stdout = io.stdout ?? process.stdout;
  const stderr = io.stderr ?? process.stderr;
  const env = io.env ?? process.env;
  const cwd = io.cwd ?? process.cwd();
  const platform = io.platform ?? process.platform;
  const spawnImpl = io.spawnImpl ?? spawn;
  const binaryAvailableImpl = io.binaryAvailableImpl ?? binaryAvailable;
  const readStdinIfPipedImpl = io.readStdinIfPipedImpl ?? readStdinIfPiped;

  if (env.CLAUDE_COMPANION_DEPTH) {
    throw new Error("claudecode-companion cannot be called recursively. CLAUDE_COMPANION_DEPTH is already set.");
  }

  const { options, positionals } = parseCommandInput(argv);
  if (options.help) {
    printUsage();
    return Promise.resolve({ status: 0, result: "", model: DEFAULT_MODEL, costUsd: 0 });
  }

  const binaryStatus = binaryAvailableImpl("claude", ["--version"], { cwd });
  if (!binaryStatus.available) {
    throw new Error(
      `Claude Code was not found on PATH (${binaryStatus.detail}). Install it from https://docs.anthropic.com/en/docs/claude-code and retry.`
    );
  }

  const prompt = resolvePrompt(positionals, options, cwd, readStdinIfPipedImpl).trim();
  if (!prompt) {
    throw new Error("Provide a prompt with an argument, piped stdin, or --prompt-file <path>.");
  }

  const targetCwd = options.cwd ? ensureAbsolutePath(cwd, options.cwd) : cwd;
  const model = options.model ? String(options.model) : DEFAULT_MODEL;
  const maxTurns = parseMaxTurns(options["max-turns"]);
  const jsonMode = Boolean(options.json);
  const launch = buildClaudeLaunch(platform);
  const child = spawnImpl(
    launch.command,
    [
      "-p",
      prompt,
      "--output-format",
      "stream-json",
      "--verbose",          // required by CC for stream-json in -p mode
      "--max-turns",
      String(maxTurns),
      "--model",
      model,
      "--allowedTools",
      buildAllowedTools(Boolean(options.write))
    ],
    {
      cwd: targetCwd,
      env: {
        ...env,
        CLAUDE_COMPANION_DEPTH: "1"
      },
      shell: launch.shell
    }
  );

  return new Promise((resolve) => {
    let stdoutBuffer = "";
    let assistantText = "";
    let finalResult = "";
    let costUsd = 0;
    let resultModel = model;
    let settled = false;

    const settle = (payload) => {
      if (settled) {
        return;
      }
      settled = true;
      resolve(payload);
    };

    child.stdout?.on("data", (chunk) => {
      stdoutBuffer += String(chunk);
      stdoutBuffer = flushJsonLines(
        stdoutBuffer,
        (event) => {
          if (event.type === "assistant") {
            const content = event.message?.content ?? [];
            const text = content
              .filter((c) => c.type === "text")
              .map((c) => String(c.text ?? ""))
              .join("");
            assistantText += text;
            if (!jsonMode && text) {
              stdout.write(text);
            }
            return;
          }

          if (event.type === "result") {
            finalResult = String(event.result ?? "");
            costUsd = Number(event.total_cost_usd ?? 0);
            const modelKeys = Object.keys(event.modelUsage ?? {});
            if (modelKeys.length > 0) {
              resultModel = modelKeys[0];
            }
          }
        },
        stderr
      );
    });

    child.stderr?.on("data", (chunk) => {
      stderr.write(chunk);
    });

    child.on("error", (error) => {
      stderr.write(`${error.message}\n`);
      process.exitCode = 1;
      settle({ status: 1, result: finalResult, model: resultModel, costUsd });
    });

    child.on("close", (code) => {
      const status = Number.isInteger(code) ? code : 1;
      if (stdoutBuffer.trim()) {
        stdoutBuffer = flushJsonLines(stdoutBuffer + "\n", (event) => {
          if (event.type === "assistant") {
            const content = event.message?.content ?? [];
            const text = content
              .filter((c) => c.type === "text")
              .map((c) => String(c.text ?? ""))
              .join("");
            assistantText += text;
            if (!jsonMode && text) {
              stdout.write(text);
            }
            return;
          }

          if (event.type === "result") {
            finalResult = String(event.result ?? "");
            costUsd = Number(event.total_cost_usd ?? 0);
            const modelKeys = Object.keys(event.modelUsage ?? {});
            if (modelKeys.length > 0) {
              resultModel = modelKeys[0];
            }
          }
        }, stderr);
      }

      if (status !== 0) {
        process.exitCode = status;
      }

      if (jsonMode) {
        stdout.write(
          `${JSON.stringify({
            status,
            result: finalResult,
            model: resultModel,
            costUsd
          })}\n`
        );
      } else if (!assistantText && finalResult) {
        stdout.write(finalResult);
      }

      settle({ status, result: finalResult, model: resultModel, costUsd });
    });
  });
}

export async function main(argv = process.argv.slice(2), io = {}) {
  const normalizedArgv = normalizeArgv(argv);
  const [subcommand, ...rest] = normalizedArgv;

  if (!subcommand || subcommand === "--help") {
    printUsage();
    return 0;
  }

  if (subcommand !== "task") {
    throw new Error(`Unsupported subcommand "${subcommand}". Use --help for usage.`);
  }

  await runTaskCommand(rest, io);
  return process.exitCode ?? 0;
}

const invokedAsScript = process.argv[1] && import.meta.url === new URL(`file://${process.argv[1]}`).href;

if (invokedAsScript) {
  main().catch((error) => {
    process.stderr.write(`${error.message}\n`);
    process.exitCode = 1;
  });
}
