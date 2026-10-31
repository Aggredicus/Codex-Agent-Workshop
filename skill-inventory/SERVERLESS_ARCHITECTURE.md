# Private node runtime moved to Local Agent Workshop

This document is a migration pointer for the CAW contributor-gateway development branch.

**CAW now owns skill taxonomy, recruitment, contributor matching, governance proposals, and the canonical [CAW–LAW work packet](../contracts/caw-law-work-packet.v1.json).**

The private SQLite node registry (`src/workshop/local_registry.py`), local CLI (`scripts/node_registry.py`), agent-version reassessment, and runtime permission plans have moved to [Local Agent Workshop](https://github.com/Aggredicus/Local-Agent-Workshop/tree/agent/caw-law-runtime-split-v01).

Read [LAW's integration documentation](https://github.com/Aggredicus/Local-Agent-Workshop/blob/agent/caw-law-runtime-split-v01/docs/CAW_LAW_INTEGRATION.md) for installation, security boundaries, and pending sandbox implementation.

The public CAW repository never stores personally identifiable inventory records or computer fingerprints. The user supplies any node/agent data directly to LAW's private local registry, which is not a source of authenticated GitHub permissions.

**Migration note:** After both pull requests are approved and merged, replace branch-specific links with stable main or tagged-release links.
