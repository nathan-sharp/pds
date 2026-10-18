# ARC PDS (Personal Data Server) Protocol - Architecture & Roadmap

## The Final Goal
The PDS Protocol is a self-hosted, offline-first, user-owned data repository and authentication node.

### Tech Stack
- Python 3.11+
- FastAPI
- SQLite (SQLAlchemy)
- Docker

### Core Systems
1. **Identity (PDS ID):**
   - A unified "PDS ID" system handling user registration.
   - OAuth2-style app authorization (issuing scoped JWTs to third-party apps).
2. **Data Vault (Zero-Knowledge CRUD):**
   - App-agnostic, zero-knowledge CRUD endpoints (e.g., `PUT /api/v1/vault/{app_id}/{collection}/{record_id}`).
   - The server blindly accepts, stores, and serves heavily encrypted blobs without decrypting them.

---

## Roadmap: Checklist of Atomic Steps

### 1. Initial Setup & Infrastructure
- [ ] Scaffold the FastAPI directory structure and base `main.py`.
- [ ] Add the basic `/ping` endpoint for health checks.
- [ ] Set up SQLAlchemy with an async SQLite engine and database session management.
- [ ] Write the `Dockerfile` for the FastAPI application.
- [ ] Write the `docker-compose.yml` to orchestrate FastAPI and SQLite.

### 2. Identity System (PDS ID)
- [ ] Create the SQLAlchemy `User` model.
- [ ] Implement secure password hashing utilities.
- [ ] Build the user registration endpoint (`POST /api/v1/auth/register`).
- [ ] Add utility functions for generating and validating JWTs.
- [ ] Implement OAuth2-style app authorization endpoints (issuing scoped JWTs).

### 3. Data Vault (Zero-Knowledge CRUD)
- [ ] Create the `VaultRecord` SQLAlchemy model (with `app_id`, `collection`, `record_id`, and `encrypted_blob`).
- [ ] Implement the Vault `PUT` endpoint (`PUT /api/v1/vault/{app_id}/{collection}/{record_id}`).
- [ ] Implement the Vault `GET` endpoint for retrieving a single record (`GET /api/v1/vault/{app_id}/{collection}/{record_id}`).
- [ ] Implement the Vault `DELETE` endpoint (`DELETE /api/v1/vault/{app_id}/{collection}/{record_id}`).
- [ ] Implement the Vault `GET` endpoint for listing records in a collection (`GET /api/v1/vault/{app_id}/{collection}`).
