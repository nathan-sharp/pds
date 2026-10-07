# ARC PDS Backend

Central authentication and blind data-synchronization server for ARC (Anthro Research Corporation) PDS ecosystem.

## Target Client Applications

1. **Chirp**: Chat and communications
2. **Burrow**: File vault and encrypted object storage
3. **Scratch**: Notes and documentation
4. **Scout**: Maps and navigation
5. **Echo**: Music and audio
6. **Flock**: Social messaging and blogging

## Architectural Principles

- **Zero-Knowledge Storage**: The PDS stores opaque encrypted blobs. It possesses no decryption keys.
- **Single Sign-On (SSO)**: Unified PDS ID authentication via OAuth 2.0 with Proof Key for Code Exchange (PKCE, RFC 7636).
- **Offline-First Synchronization**: Clients maintain local encrypted databases and synchronize delta changes via monotonic version counters and tombstones.

## System Documentation

Comprehensive technical specifications and architectural decision records are maintained in the `docs/` directory:
- [System Architecture](file:///c:/Users/User/Downloads/pds/docs/ARCHITECTURE.md): Dual-zone storage, W3C DIDs, S2S federation, and event streaming.
- [Architecture Decision Records (ADRs)](file:///c:/Users/User/Downloads/pds/docs/DECISIONS.md): Foundational design decisions and architectural trade-offs.
- [Development Roadmap](file:///c:/Users/User/Downloads/pds/docs/ROADMAP.md): Phased engineering milestones and implementation progress.
- [Creator Monetization Engine](file:///c:/Users/User/Downloads/pds/docs/MONETIZATION.md): Local budget pools, HTTP 402, and L402 micropayment access gating.

## Local Deployment Instructions

### Option 1: Docker Compose (Recommended)

1. Copy the example configuration file:
   ```bash
   cp .env.example .env
   ```
2. Build and start the services:
   ```bash
   docker compose up --build -d
   ```
3. Verify service health:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```
4. Access OpenAPI interactive documentation:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

### Option 2: Local Virtual Environment

1. Create a Python 3.12 virtual environment:
   ```bash
   python -m venv .venv
   ```
2. Activate the virtual environment:
   - Linux/macOS: `source .venv/bin/activate`
   - Windows PowerShell: `.\.venv\Scripts\Activate.ps1`
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

## Security Verification Notice

Supply chain security notice: Verify the integrity and authenticity of all third-party dependencies listed in `requirements.txt` prior to production deployment.
