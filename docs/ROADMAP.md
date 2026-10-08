# ARC PDS Development Roadmap

This document outlines the phased engineering milestones for the ARC (Anthro Research Corporation) Personal Data Server (PDS).

---

## Milestone Overview

| Phase | Milestone Name | Primary Focus | Status |
| :---: | :--- | :--- | :---: |
| **1** | **Core Node & Private Storage** | Containerized FastAPI runtime, PDS ID authentication, Argon2id, OAuth 2.0 PKCE, and blind E2EE sync blobs. | **Completed** |
| **2** | **Decentralized Identity & Dual-Zone Storage** | W3C `did:web` documents, Ed25519 and X25519 keys, and signed public federated record storage. | **Up Next** |
| **3** | **Event Streaming & Processing Engine** | Real-time WebSocket event firehose and HMAC-signed webhook dispatcher. | **Planned** |
| **4** | **Server-to-Server (S2S) Federation** | RFC 9421 HTTP Message Signatures, cross-node discovery, and inbox record synchronization. | **Planned** |
| **5** | **Creator Monetization & HTTP 402** | Local budget manager, L402 challenge/response middleware, and Layer-2 micropayment integrations. | **Parked (Deferred)** |

---

## Detailed Milestone Objectives

### Phase 1: Core Node & Private Storage (Status: Completed)
- [x] Docker and Docker Compose orchestration with PostgreSQL 16.
- [x] Unprivileged container runtime with health checks.
- [x] PDS ID user registration with Argon2id password hashing (`m=64 MiB`, `t=3`, `p=4`).
- [x] OAuth 2.0 with PKCE authorization code flow (RFC 7636).
- [x] JWT access token issuance with rotating refresh tokens.
- [x] Opaque End-to-End Encrypted (E2EE) data push/pull endpoints for private suite apps.

### Phase 2: Decentralized Identity & Dual-Zone Storage (Status: Up Next)
- [ ] Database schema for cryptographic identity key pairs (Ed25519 signing key, X25519 encryption key).
- [ ] W3C DID document resolver at `/.well-known/did.json` and `/api/v1/identity/{did}`.
- [ ] Public federated record storage schema for Flock and public collections.
- [ ] Ingestion endpoint with Ed25519 cryptographic signature verification (`POST /api/v1/records`).
- [ ] Account migration export and signature verification mechanism.

### Phase 3: Event Streaming & Processing Engine (Status: Planned)
- [ ] In-memory / database pub-sub event dispatcher.
- [ ] Real-time WebSocket firehose endpoint (`WS /api/v1/events/firehose`).
- [ ] Webhook subscription registry with retry queues (`POST /api/v1/webhooks/subscriptions`).
- [ ] HMAC-SHA256 signature generation for webhook payload delivery.

### Phase 4: Server-to-Server (S2S) Federation (Status: Planned)
- [ ] HTTP Message Signature middleware implementing RFC 9421.
- [ ] Server identity certificate generation and verification.
- [ ] Cross-node inbox endpoint (`POST /api/v1/federation/inbox`).
- [ ] Peer discovery and public key cache manager.

### Phase 5: Creator Monetization & HTTP 402 (Status: Parked / Deferred)
- [ ] User monthly budget management database models and API.
- [ ] HTTP 402 challenge generator with Macaroon caveat verification.
- [ ] L402 client middleware for automatic payment and preimage redemption.
- [ ] Consumption tallying engine with local proportional distribution.
