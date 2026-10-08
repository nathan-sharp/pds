"""API Router aggregation for V1 endpoints."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, health, identity, oauth, records, sync

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["PDS Authentication"])
api_router.include_router(oauth.router, prefix="/oauth", tags=["OAuth 2.0 PKCE"])
api_router.include_router(sync.router, prefix="/sync", tags=["Blind E2EE Sync"])
api_router.include_router(identity.router, prefix="/identity", tags=["W3C Decentralized Identity"])
api_router.include_router(records.router, prefix="/records", tags=["Zone 2 Public Federated Records"])
