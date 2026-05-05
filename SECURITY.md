# Security Policy

This repo is intended to stay private while Octopus V3 is planned.

Do not commit:

- API keys, tokens, passwords, or private keys
- `.env`, `.claude`, local chat/session state, or editor state
- SQLite databases, logs, memory journals, vault exports, or benchmark output with raw prompts
- Proprietary model files, weights, checkpoints, or local LM Studio state

Daily checks should scan the full Git history and current tree for secret patterns and accidental local state.

