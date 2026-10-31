# Serverless Skill and Node Registry (v0.1)

Codex Agent Workshop needs **no custom server, database daemon, or paid coordination platform**.

## Sources of truth

| Information | Location | Authority |
|---|---|---|
| Skill definitions, team policy, and governance proposals | Git-tracked JSON and SKILL.md | Reviewed Git changes |
| People, computers, agents, inventory assertions, and proposals | Private local SQLite | Local-only assertions |
| Work status, PR reviews, authorized merges, and collaboration | GitHub Issues and protected PR workflows | Authenticated GitHub service |

GitHub is itself a hosted service. All local registry operations work offline; multi-computer synchronization requires GitHub connectivity or a separately designed peer-transfer protocol. No new CAW server is required.

## Local identities

Each human, physical computer installation, and agent instance receives a random, opaque UUID-based ID with its own prefix. These IDs do not reveal a name, IP address, MAC address or hardware serial. An agent points to an enrolled local human operator and computer and declares a source, version, and SHA-256 artifact digest. These declarations are not independent identity or cryptographic attestation, and cannot grant repository permissions.

The SQLite database resides only in skill-inventory/private/nodes.sqlite3 (ignored by Git), with restrictive local file permissions where supported. Local state is not encrypted by SQLite; use encrypted storage and private backups when necessary.

When a model, runtime, or artifact digest changes, the agent keeps its stable local ID but is marked for reassessment. The version history is recorded, current skill assertions are cleared, and pending permission proposals are invalidated.

## Commands (Python 3.11+, no extra runtime packages)

    python scripts/node_registry.py summary
    python scripts/node_registry.py enroll --kind human
    python scripts/node_registry.py enroll --kind computer

Use the real IDs printed locally when registering an agent:

    python scripts/node_registry.py enroll --kind agent --operator-id HUMAN_ID --computer-id COMPUTER_ID --source codex --version 1.0 --digest sha256:HEX_DIGEST
    python scripts/node_registry.py inventory --id AGENT_ID --skill python --skill agent-orchestration
    python scripts/node_registry.py propose --id AGENT_ID --skill python --action pr.propose
    python scripts/node_registry.py upgrade --id AGENT_ID --source codex --version 1.1 --digest sha256:NEW_HEX_DIGEST

Use 64 lowercase hexadecimal characters after the 'sha256:' prefix. Never publish real node IDs or record private contact information. Identifiers are pseudonymous and may be correlatable if shared.

## Privilege enforcement

Local SQLite records skill claims and permission **proposals only**. It cannot authorize GitHub PR review, merging, credentials, or running privileged tools. A role self-assigned by an agent is never effective authority.

To enforce policy, use protected default branches, GitHub's verified actor identity, required human review, and least-privilege credentials on isolated execution environments. Approvals and role eligibility are evaluated independently from skill claims. A self-declared checksum does not authenticate an agent version.

Agents running under the same OS user can potentially access the same SQLite database. For real isolation, run them with separate sandbox/OS privileges. SQLite event history is a local convenience, not tamper-proof.

## Concurrency and synchronization

SQLite enables multiple readers and one serialized writer on a single computer. Local WAL must not be shared over SMB, NFS, or synchronized as a live SQLite/WAL file. Each computer maintains its own independent database.

Shared information is transferred as reviewed, non-sensitive JSON manifests and normal Git changes. Work assignments and decisions live on GitHub. If computers are offline, independently prepared actions cannot be assumed mutually synchronized. Conflicting actions require normal Git merge/review.

The public offline HTML contributor gateway needs no backend and continues to work as a static document. The SQLite CLI requires Python and is not yet an Android/iOS browser-storage implementation; future IndexedDB adapters may be added.

## Tests and extensions

Run:

    pytest -q tests/test_local_registry.py
    pytest -q

Retain a versioned SQLite schema and reversible migrations. Future additions may include signed agent origin attestations, safe capability export, GitHub identity adapters, cross-device conflict reconciliation and browser-local storage. Each should have adversarial tests and independent security review.
