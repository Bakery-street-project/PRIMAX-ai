# 🌟 Premium Features

[![Sponsor BoozeLee](https://img.shields.io/badge/Sponsor-BoozeLee-ea4aaa?logo=github-sponsors&logoColor=white&style=for-the-badge)](https://github.com/sponsors/BoozeLee)

Core features are **always free**. Premium tiers unlock advanced capabilities and direct support.

---

## Feature Comparison

| Feature | Free | $5 Community | $12 Pro | $25 Gold | $50 Enterprise |
|---------|:----:|:---:|:---:|:---:|:---:|
| Core functionality | ✅ | ✅ | ✅ | ✅ | ✅ |
| Bug reports & issues | ✅ | ✅ | ✅ | ✅ | ✅ |
| Community discussion | ✅ | ✅ | ✅ | ✅ | ✅ |
| Sponsor badge | — | ✅ | ✅ | ✅ | ✅ |
| README shoutout | — | ✅ | ✅ | ✅ | ✅ |
| Early access to releases | — | — | ✅ | ✅ | ✅ |
| Priority issue responses | — | — | ✅ | ✅ | ✅ |
| Private Discord access | — | — | ✅ | ✅ | ✅ |
| Name/logo in README | — | — | — | ✅ | ✅ |
| Monthly 1-on-1 check-in | — | — | — | ✅ | ✅ |
| Roadmap voting | — | — | — | ✅ | ✅ |
| Priority feature requests | — | — | — | — | ✅ |
| Logo on landing pages | — | — | — | — | ✅ |
| Dedicated support channel | — | — | — | — | ✅ |
| **Lifetime Supporter** | — | — | — | — | $100 one-time |
| Hall of Fame listing | — | — | — | — | ✅ (lifetime) |
| All private repo access | — | — | — | — | ✅ (lifetime) |

---

## How to Unlock Premium

1. Visit **[github.com/sponsors/BoozeLee](https://github.com/sponsors/BoozeLee)**
2. Choose your tier and complete payment via GitHub
3. Features activate automatically — GitHub verifies your sponsorship
4. For private Discord, open an issue with your GitHub handle after sponsoring

---

## Sponsor Verification (for APIs)

This project uses `sponsor_check.py` to verify GitHub Sponsors status at runtime.

```python
from src.sponsor_check import require_sponsor

@require_sponsor(min_tier_usd=12)  # Pro Backer+
async def premium_endpoint(username: str, token: str):
    ...
```

Verification hits the GitHub GraphQL API (`isSponsoringViewer`) — no manual approval needed.

---

## Enterprise & Custom Licensing

For teams, hospitals, or enterprise deployments needing:
- SLA guarantees
- Custom integrations
- On-premise deployment
- HIPAA / GDPR compliance consulting

Contact: **kiliaanv2@gmail.com**

---

_[github.com/sponsors/BoozeLee](https://github.com/sponsors/BoozeLee) · Belgium 🇧🇪_
