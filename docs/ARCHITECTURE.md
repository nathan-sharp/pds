# ARC PDS System Architecture Specification

## 1. Executive Overview

This document specifies the architecture of the ARC (Anthro Research Corporation) Personal Data Server (PDS). 
The ARC PDS provides self-hosted identity, storage, and processing services. 
The system operates as an open alternative to centralized cloud platform accounts. 
The architecture supports six primary client applications:
1. **Chirp**: Encrypted chat and communication.
2. **Burrow**: Encrypted file storage and object vault.
3. **Scratch**: Encrypted notes and structured documents.
4. **Scout**: Geospatial mapping and routing.
5. **Echo**: Audio storage and streaming.
6. **Flock**: Public microblogging and social networking.

---

## 2. Core Architectural Pillars

```
                          ┌─────────────────────────────────────────┐
                          │         ARC PDS (Node A)                │
                          │                                         │
┌──────────────────┐      │  ┌───────────────────────────────────┐  │      ┌──────────────────┐
│   Private App    │◄────┼─►│     Private Zone (Opaque E2EE)     │  │      │   Private App    │
│ (Burrow/Scratch) │      │  │ (Ciphertext, IV, Auth Tag, Vers)  │  │      │     (Chirp)      │
└──────────────────┘      │  └───────────────────────────────────┘  │      └──────────────────┘
                          │                                         │
┌──────────────────┐      │  ┌───────────────────────────────────┐  │      ┌──────────────────┐
│  Public/Social   │◄────┼─►│     Public Zone (Federated)        │  │      │ Third-Party App  │
│   App (Flock)    │      │  │  (Signed JSON, DIDs, Ed25519)     │  │◄────┼─► (Open API SSO) │
└──────────────────┘      │  └─────────────────┬─────────────────┘  │      └──────────────────┘
                          │                    │                    │
                          │  ┌─────────────────▼─────────────────┐  │
                          │  │  Event Stream Engine (WebSockets) │  │
                          │  └─────────────────┬─────────────────┘  │
                          └────────────────────┼────────────────────┘
                                               │
                                 S2S Federation (Ed25519 Signed)
                                               │
                          ┌────────────────────▼────────────────────┐
                          │         ARC PDS (Node B)                │
                          │  - Resolves did:web from Node A         │
                          │  - Ingests verified public records      │
                          └─────────────────────────────────────────┘
```

### 2.1. Dual-Zone Storage Partitioning

The ARC PDS isolates private data from federated public records through two distinct storage zones:

| Metric / Attribute | Zone 1: Private Vault | Zone 2: Public Federated Repository |
| :--- | :--- | :--- |
| **Data Scope** | Files, private notes, direct messages, media files. | Public microblogs, profile identity, social graph. |
| **Encryption State** | End-to-End Encrypted (E2EE) ciphertext. | Plaintext JSON with cryptographic signatures. |
| **Server Visibility** | Zero-knowledge (opaque bytes, initialization vector, authentication tag). | Full read visibility for query indexing and federation relay. |
| **Cryptographic Primitive** | Client-side Authenticated Encryption with Associated Data (AEAD). | Edwards-curve Digital Signature Algorithm (Ed25519). |
| **Access Control** | Single-user authentication via OAuth 2.0 and PKCE. | Public read; signed write per Decentralized Identifier (DID). |

### 2.2. Portable Identity System

1. **Identity Standard**: World Wide Web Consortium (W3C) Decentralized Identifiers (DIDs).
2. **DID Format**: `did:web:<domain>:users:<username>`.
3. **Cryptographic Key Pairs**:
   - `signingKey`: Ed25519 public key for signing public records and HTTP messages.
   - `encryptionKey`: Curve25519 (X25519) public key for inter-user encrypted key exchange.
4. **Account Migration Protocol**:
   - The user generates an update statement on Server A.
   - The user signs the statement with their primary Ed25519 identity key.
   - The statement points resolvers to Server B.
   - External nodes verify the signature and update routing pointers.

### 2.3. Server-to-Server (S2S) Federation Protocol

1. **Transport Layer**: Secure Hypertext Transfer Protocol (HTTPS) REST for mutations; WebSockets for real-time synchronization.
2. **Authentication Standard**: HTTP Message Signatures (RFC 9421).
   - Sender signs HTTP request headers (`(request-target)`, `host`, `date`, `digest`) with its Ed25519 server key.
   - Receiver verifies the signature against the sender's public DID document.
3. **Core Endpoints**:
   - `GET /.well-known/did.json`: Exposes server public identity document.
   - `POST /api/v1/federation/inbox`: Ingests foreign public records.
   - `GET /api/v1/federation/records`: Exposes public records by collection.
   - `WS /api/v1/federation/stream`: Broadcasts real-time public updates.

### 2.4. Processing and Extension Engine

1. **Authentication Hub**: OAuth 2.0 with Proof Key for Code Exchange (PKCE, RFC 7636).
2. **Event Delivery**:
   - WebSockets stream real-time events to connected clients.
   - Webhooks deliver signed JSON payloads to registered external microservices.
3. **Compute Isolation**: The PDS maintains data persistence and event dispatching. The server offloads complex compute to authorized client workers.

---

## 3. ISO/IEC 25010 Quality Characteristics Evaluation

| Quality Characteristic | Architectural Decision | Verification Method |
| :--- | :--- | :--- |
| **Maintainability** | Domain-Driven Layering (`api`, `core`, `db`, `models`, `schemas`). | Unit test suite covers each isolated module. |
| **Reliability** | Monotonic sequence counters and tombstone flags. | Concurrent multi-client sync tests verify convergence. |
| **Performance Efficiency** | Asynchronous non-blocking I/O with connection pools. | Benchmark confirms sub-10ms response times under load. |
| **Security** | Zero-Knowledge Private Storage & Argon2id hashing. | Automated OWASP ASVS compliance scan. |
