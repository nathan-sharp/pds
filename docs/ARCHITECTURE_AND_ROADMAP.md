# Architecture and Roadmap for PDS Protocol

## The Final Goal (The PDS Protocol)

The Personal Data Server (PDS) is a self-hosted, offline-first, user-owned data repository and authentication node.

### Core Architecture

- **Tech Stack:** Python 3.11+, FastAPI, SQLite (SQLAlchemy), Docker.
- **Identity:** A unified "PDS ID" system handling user registration and OAuth2-style app authorization. It issues scoped JWTs to third-party applications to guarantee secure access control.
- **Data Vault:** App-agnostic, zero-knowledge CRUD endpoints (e.g., `PUT /api/v1/vault/{app_id}/{collection}/{record_id}`). The server blindly accepts, stores, and serves heavily encrypted blobs without decrypting them.

---

## Roadmap / Implementation Checklist

The implementation is broken down into small, atomic tasks to facilitate a daily execution loop.

### 1. Project Initialization & Infrastructure
- [ ] Scaffold the FastAPI directory structure and define base configuration.
- [ ] Create basic `/api/v1/health` endpoint and tests.
- [ ] Write the `Dockerfile` and `docker-compose.yml` for isolated deployments.
- [ ] Initialize the SQLAlchemy database connection (SQLite) and base ORM models.

### 2. Identity System (PDS ID & Auth)
- [ ] Create the SQLAlchemy `User` model.
- [ ] Implement password hashing (Argon2id) and user registration endpoint.
- [ ] Add the JWT generation and verification utility functions.
- [ ] Build the authentication endpoint (`POST /auth/token`) to issue access tokens.
- [ ] Define and implement the OAuth2-style app authorization flow (issuing scoped JWTs).

### 3. Data Vault (Zero-Knowledge Storage)
- [ ] Create the SQLAlchemy `EncryptedSyncRecord` (Vault) model.
- [ ] Implement the `PUT /api/v1/vault/{app_id}/{collection}/{record_id}` endpoint (Store encrypted blob).
- [ ] Implement the `GET /api/v1/vault/{app_id}/{collection}/{record_id}` endpoint (Retrieve encrypted blob).
- [ ] Implement the `DELETE /api/v1/vault/{app_id}/{collection}/{record_id}` endpoint (Tombstone/Delete record).
- [ ] Implement a sync/list endpoint to fetch records based on a monotonic version counter (for offline-first synchronization).

### 4. Hardening & Polish
- [ ] Implement rate limiting and request validation middlewares.
- [ ] Finalize the OpenAPI documentation (Swagger/ReDoc).
- [ ] Comprehensive test suite execution (CI/CD setup).
