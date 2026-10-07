# ARC PDS Creator Monetization Specification

## 1. Executive Summary

This document specifies the decentralized creator monetization engine for the ARC (Anthro Research Corporation) Personal Data Server (PDS).
The architecture provides direct compensation for content creators across applications (such as Echo and Flock) without advertisements or centralized corporate intermediaries.

---

## 2. Core Economic Model: Local User Budget Pools

Centralized platforms (Spotify, YouTube Premium) aggregate user subscriptions into a global corporate pool. 
In a decentralized network, a global pool allows malicious actors to execute Sybil attacks by simulating views to drain shared funds.

The ARC PDS implements **Local User Budget Pools**:
1. Each user voluntarily configures a monthly budget inside their own PDS (e.g., $B = 10.00\text{ USD}$).
2. The user's PDS logs consumption units ($V_i$) for each creator node $i \in \{1, \dots, n\}$.
3. At settlement time, the user's PDS distributes payments ($P_i$) strictly from the user's own funds:

$$V_{\text{total}} = \sum_{k=1}^{n} V_k$$

$$P_i = B \times \left( \frac{V_i}{V_{\text{total}}} \right)$$

### 2.1. Attack Immunity Analysis

- **Sybil Resistance**: A bot operator generating artificial views on Creator X only consumes funds from the bot's own wallet.
- **Budget Protection**: Total disbursements cannot exceed the user's defined allocation ($B$).
- **No Central Intermediary**: The user's PDS executes the calculation directly without platform commissions.

---

## 3. Technical Protocol: HTTP 402 and L402 Access Gating

Creators gate premium content (such as high-bitrate audio on Echo or long-form essays on Flock) using Hypertext Transfer Protocol (HTTP) status code `402 Payment Required`.

### 3.1. Protocol Exchange Sequence

```
Client App (Echo/Flock)               Creator PDS                     Payment Rail (LN/ILP)
       │                                   │                                    │
       ├─── 1. GET /media/track.flac ──────►│                                    │
       │                                   │                                    │
       │◄── 2. HTTP 402 Payment Required ──┤                                    │
       │       WWW-Authenticate: L402      │                                    │
       │       macaroon="...", invoice="..."│                                    │
       │                                   │                                    │
       ├──── 3. Pay Micropayment (e.g. 50 sats / 0.02 USD) ────────────────────►│
       │◄─── 4. Settlement Preimage (Cryptographic Proof) ──────────────────────┤
       │                                   │                                    │
       ├─── 5. GET /media/track.flac ──────►│                                    │
       │       Authorization: L402         │                                    │
       │       macaroon:preimage           │                                    │
       │                                   ├── Verify Preimage                  │
       │◄── 6. 200 OK (Media Payload) ─────┤                                    │
```

1. **Unauthenticated Query**: The client requests gated media.
2. **Challenge Generation**: The creator node returns `HTTP 402` with an L402 challenge containing:
   - A cryptographic Macaroon specifying resource caveats (URI, expiration timestamp).
   - A payment invoice (such as a Lightning Network invoice).
3. **Automated Settlement**: The client's PDS evaluates the price against the user's budget rules and executes the micro-transaction.
4. **Receipt Generation**: The payment rail returns a cryptographic preimage proving settlement.
5. **Authenticated Request**: The client repeats the request with the `Authorization: L402 <macaroon>:<preimage>` header.
6. **Stateless Verification**: The creator node verifies the HMAC signature of the macaroon and confirms the preimage SHA-256 hash without querying a central database.

---

## 4. Privacy and Offline Access Safeguards

### 4.1. Privacy Preservation via Blind Tokens
- Direct payments must not expose user browsing history to third-party nodes.
- When settling invoices, the client PDS strips user identity metadata (such as username and DID).
- Creator nodes record only the payment preimage hash, verifying financial settlement without identifying the consumer.

### 4.2. Offline Consumption via Ticket-Granting Tokens (TGT)
- When preparing for offline operation, client applications request a batch of time-bound access tickets while connected.
- The client PDS pre-settles the ticket bundle.
- During offline playback, the client presents the stored ticket to unlock cached local assets without network access.
