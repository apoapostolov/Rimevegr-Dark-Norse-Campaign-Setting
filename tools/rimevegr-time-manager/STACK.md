# Rimevegr Time Manager Stack

## Recommended Stack

### Frontend

- React
- TypeScript
- Vite
- TanStack Router
- TanStack Query
- Zod for client-side contract validation
- Zustand or Jotai for light local UI state
- Monaco or CodeMirror only for advanced diff views, not as the main UI

### Backend / Simulation Service

- Python 3.12+
- FastAPI for local API surface
- Pydantic for request and response contracts
- `ruamel.yaml` for round-trip YAML preservation
- `jsonpatch` or explicit patch objects for reversible transaction records
- `orjson` for fast local state serialization

### Storage

- append-only transaction JSON files
- compressed snapshot files
- file-hash manifest for integrity verification
- optional SQLite index for search, transaction metadata, and branch lookup

## Why Not Pure TypeScript

Pure TypeScript would fight the current codebase.

- the world simulation logic already exists in Python
- YAML preservation is safer with `ruamel.yaml`
- reusing existing Python simulation adapters reduces duplication and drift

So the right split is:

- TypeScript for product UX
- Python for data authority and simulation execution

## Runtime Shape

### Local app mode

- Vite frontend
- FastAPI local server
- both launched together through one dev command later

### Packaging target

- desktop-like local tool first
- Tauri is acceptable later if distribution matters
- avoid Electron unless there is a real need

## Core Backend Modules

- `state_loader`
- `snapshot_store`
- `transaction_log`
- `patch_engine`
- `time_cursor`
- `adapter_registry`
- `narrative_builder`
- `integrity_guard`
- `branch_manager`

## Adapter Contract

Each simulation domain should register a time adapter with:

- supported granularities
- read files
- write files
- deterministic requirements
- preview capability
- apply capability
- inverse generation capability
- validation hooks

## Testing Standard

- unit tests for patch generation and inverse patches
- golden tests for narrative output
- deterministic replay tests using fixed seeds
- corruption tests for hash mismatch and partial write failure
- contract tests for every adapter

## Production Readiness Requirements

- atomic writes
- temp-file swap, never in-place blind overwrite
- snapshot before commit
- hash verification before undo
- structured error reporting
- forced preview for high-risk operations
