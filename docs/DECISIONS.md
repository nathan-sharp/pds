# Architecture Decision Records (ADRs)

This document records the foundational architectural decisions for the ARC (Anthro Research Corporation) Personal Data Server (PDS).

---

## ADR-001: Standardization on ARC PDS Naming

- **Status**: Accepted
- **Context**: The project originally used the framework name P.A.W.S. (Platform Agnostic Wrapper Service). The system required a distinct brand identity representing Anthro Research Corporation.
- **Decision**: Replace all references to P.A.W.S. with **ARC PDS**.
- **Consequences**:
  - The project, repository, environment configurations, and documentation now use ARC PDS.
  - Client application models identify the ecosystem as the ARC suite.

---

## ADR-002: W3C Decentralized Identifiers (DIDs) for Identity and Portability

- **Status**: Accepted
- **Context**: Centralized ecosystems lock user identity to specific domains. If a server deactivates, the user loses their identity and social connections.
- **Decision**: Adopt the World Wide Web Consortium (W3C) Decentralized Identifier standard using the `did:web` method mapped to domain handles.
- **Consequences**:
  - Identities resolve via standard cryptographic DID documents.
  - Users sign account migration statements using their primary Ed25519 identity key.
  - Host server migrations preserve user identity and cryptographic signatures.

---

## ADR-003: Dual-Zone Storage Partitioning

- **Status**: Accepted
- **Context**: The ARC suite includes private personal tools (Burrow, Scratch, Chirp) and public social platforms (Flock). Storing all data in one format creates privacy leaks or prevents federation.
- **Decision**: Implement two explicit storage zones within the PDS database:
  1. **Zone 1 (Private Vault)**: Stores opaque End-to-End Encrypted (E2EE) ciphertext. The server possesses no decryption keys.
  2. **Zone 2 (Public Repository)**: Stores plaintext JSON records signed by the author's Ed25519 key. The server exposes this data for federation.
- **Consequences**:
  - Zero-knowledge confidentiality protects private files and communications.
  - Public microblog posts remain discoverable, indexable, and verifiable across nodes.

---

## ADR-004: Custom Server-to-Server (S2S) Federation Protocol

- **Status**: Accepted
- **Context**: Existing federation protocols (ActivityPub, Matrix) contain legacy complexity and state-resolution overhead. The ARC PDS requires a lightweight, auditable federation protocol.
- **Decision**: Implement a custom S2S protocol using HTTPS REST for mutations and WebSockets for real-time streams, authenticated via HTTP Message Signatures (RFC 9421) and Ed25519 keys.
- **Consequences**:
  - Eliminates shared secrets between federated nodes.
  - Provides cryptographic non-repudiation for all delivered public records.
  - Requires maintaining custom client and server synchronization logic.

---

## ADR-005: Event-Driven Processing Engine

- **Status**: Accepted
- **Context**: Self-hosted servers possess finite Central Processing Unit (CPU) and memory capacity. Executing heavy compute inside the API container degrades core storage throughput.
- **Decision**: Restrict the PDS core to data storage and event broadcasting. Expose real-time WebSocket firehose endpoints and signed HTTP webhooks for external workers.
- **Consequences**:
  - Heavy tasks (audio transcoding, search indexing, machine learning) execute in separate worker containers.
  - PDS server core remains fast, deterministic, and memory-efficient.

---

## ADR-006: Decentralized Creator Monetization via Local Pools and HTTP 402

- **Status**: Deferred (Parked)
- **Context**: Open networks (Mastodon, Bluesky) struggle to attract professional creators due to the lack of built-in monetization. Global payment pools suffer from Sybil bot-farming attacks.
- **Decision Deferred**: Monetization mechanics are parked to prioritize core decentralized identity, dual-zone storage, and federation protocols.
  1. **Local User Pools**: Users fund a voluntary monthly budget inside their own PDS. Funds split proportionally only among creators that specific user consumed.
  2. **HTTP 402 Protocol**: Creators gate exclusive content with HTTP status code 402 (`Payment Required`).
  3. **Layer-2 Micropayments**: Clients settle sub-cent payments via the Lightning Network (L402 standard) or local voucher tokens.
- **Consequences**:
  - Sybil attacks cannot drain global funds; attackers cannot steal other users' balances.
  - Creators receive compensation per view without relying on advertising networks.
  - Requires integration of Layer-2 micropayment rails or payment channel engines.
