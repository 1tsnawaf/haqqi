"""
Rights radar — proactive discovery.
Surface entitlements the user did not ask about. Owned by P1.
"""
from app.schemas import Profile, Citation


def find_unclaimed_rights(profile: Profile) -> list[Citation]:
    """
    TODO (P1): based on the profile (tenure, status, salary), retrieve and return
    entitlements the user likely has but didn't mention — end-of-service pay,
    unused-leave payout, notice period, overtime, etc.
    """
    return []
