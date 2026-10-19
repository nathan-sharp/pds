# ARCHITECTURE AND ROADMAP

## The Final Goal (The PDS Protocol)

**Tech Stack:** Python 3.11+, FastAPI, SQLite (SQLAlchemy), Docker.

**Identity:** A unified "PDS ID" system handling user registration and OAuth2-style app authorization (issuing scoped JWTs to third-party apps).

**Data Vault:** App-agnostic, zero-knowledge CRUD endpoints (e.g., `PUT /api/v1/vault/{app_id}/{collection}/{record_id}`). The server blindly accepts, stores, and serves heavily encrypted blobs without decrypting them.

## Roadmap Checklist

- [ ] Scaffold the FastAPI directory structure and ping endpoint
- [ ] Create the SQLAlchemy User model
- [ ] Write the Dockerfile
- [ ] Add the JWT generation utility
- [ ] Implement Identity PDS ID user registration endpoint
- [ ] Implement OAuth2-style app authorization endpoint
- [ ] Implement Data Vault zero-knowledge CRUD endpoint: PUT
- [ ] Implement Data Vault zero-knowledge CRUD endpoint: GET
- [ ] Implement Data Vault zero-knowledge CRUD endpoint: DELETE
- [ ] Implement Data Vault zero-knowledge CRUD endpoint: LIST
