"""
Demo seed script — creates a demo company + admin user with known credentials.

Usage (from project root):
    python scripts/seed_demo.py

Safe to run multiple times — skips creation if the demo account already exists.
"""

import asyncio
import sys
from pathlib import Path

# Allow imports from the project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.auth import hash_password
from app.db.repositories.company_repo import CompanyRepository, CompanyUserRepository
from app.db.session import AsyncSessionLocal
from app.models.company import CompanyType, SubscriptionTier
from app.models.company_user import UserRole

DEMO_EMAIL = "demo@f1scouts.com"
DEMO_PASSWORD = "Demo1234!"
DEMO_COMPANY = "Demo F1 Scouts"


async def seed():
    async with AsyncSessionLocal() as session:
        company_repo = CompanyRepository(session)
        user_repo = CompanyUserRepository(session)

        existing = await company_repo.get_by_contact_email(DEMO_EMAIL)
        if existing:
            print("Demo account already exists — no changes made.")
            print_credentials()
            return

        company = await company_repo.create(
            name=DEMO_COMPANY,
            contact_email=DEMO_EMAIL,
            company_type=CompanyType.OTHER,
            subscription_tier=SubscriptionTier.ENTERPRISE,
        )
        # Set high quota so it never runs out during a demo
        await company_repo.update(company, query_quota_monthly=9999, is_verified=True)

        await user_repo.create(
            company_id=company.id,
            email=DEMO_EMAIL,
            hashed_password=hash_password(DEMO_PASSWORD),
            role=UserRole.ADMIN,
        )

        await session.commit()
        print("Demo account created successfully.")
        print_credentials()


def print_credentials():
    print("\n--- Demo Login Credentials ---")
    print(f"  Email:    {DEMO_EMAIL}")
    print(f"  Password: {DEMO_PASSWORD}")
    print(f"  Endpoint: POST /api/v1/auth/login")
    print("------------------------------\n")


if __name__ == "__main__":
    asyncio.run(seed())
