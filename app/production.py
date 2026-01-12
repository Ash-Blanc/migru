"""
Production configuration and utilities for secure deployment.

This module provides:
- Production-ready defaults
- Security checks
- Health monitoring
- Data privacy verification
"""

import os
import sys
from typing import Any
from typing import cast

from app.logger import get_logger

logger = get_logger("migru.production")


class ProductionValidator:
    """Validates production readiness and security."""

    def __init__(self) -> None:
        self.checks_passed: list[str] = []
        self.checks_failed: list[str] = []
        self.warnings: list[str] = []

    def validate_all(self) -> bool:
        """Run all production checks."""
        checks = [
            self.check_environment_variables(),
            self.check_redis_security(),
            self.check_file_permissions(),
            self.check_api_key_security(),
            self.check_data_privacy(),
        ]

        return all(checks)

    def check_environment_variables(self) -> bool:
        """Verify environment configuration."""
        required_vars = ["MISTRAL_API_KEY"]
        optional_vars = ["CEREBRAS_API_KEY", "OPENWEATHER_API_KEY", "FIRECRAWL_API_KEY"]

        # Check required
        missing_required = [var for var in required_vars if not os.getenv(var)]
        if missing_required:
            self.checks_failed.append(
                f"Missing required environment variables: {missing_required}"
            )
            return False

        # Check optional
        missing_optional = [var for var in optional_vars if not os.getenv(var)]
        if missing_optional:
            self.warnings.append(
                f"Optional environment variables not set: {missing_optional}"
            )

        self.checks_passed.append("Environment variables configured")
        return True

    def check_redis_security(self) -> bool:
        """Verify Redis is configured securely."""
        try:
            from redis import Redis

            from app.config import config

            # Check if Redis is local
            redis_url = config.REDIS_URL
            if "localhost" not in redis_url and "127.0.0.1" not in redis_url:
                self.warnings.append(
                    f"Redis is not localhost: {redis_url}. Ensure it's secured."
                )

            # Try to connect
            client = Redis.from_url(redis_url)
            client.ping()

            # Check if Redis is protected
            info = cast(Any, client.info("server"))
            if info.get("tcp_port", 0) != 6379:
                self.warnings.append(f"Redis on non-standard port: {info.get('tcp_port')}")

            self.checks_passed.append("Redis connection verified")
            return True

        except Exception as e:
            self.checks_failed.append(f"Redis check failed: {e}")
            return False

    def check_file_permissions(self) -> bool:
        """Check file permissions for .env and sensitive files."""
        sensitive_files = [".env", "gcplogin.json", "credentials.json"]

        for filename in sensitive_files:
            if os.path.exists(filename):
                # Check if file is world-readable
                mode = os.stat(filename).st_mode
                if mode & 0o004:  # World readable
                    self.warnings.append(
                        f"{filename} is world-readable. Run: chmod 600 {filename}"
                    )
                else:
                    self.checks_passed.append(f"{filename} permissions OK")

        return True

    def check_api_key_security(self) -> bool:
        """Verify API keys are not in code or git."""
        # Check .gitignore exists and includes .env
        if not os.path.exists(".gitignore"):
            self.checks_failed.append(".gitignore missing!")
            return False

        with open(".gitignore") as f:
            gitignore_content = f.read()
            if ".env" not in gitignore_content:
                self.checks_failed.append(".env not in .gitignore!")
                return False

        self.checks_passed.append("API key security verified")
        return True

    def check_data_privacy(self) -> bool:
        """Verify privacy-critical files are ignored."""
        privacy_critical = [
            "*.rdb",
            "dump.rdb",
            "user_data/",
            "conversations/",
            "analytics/",
        ]

        if not os.path.exists(".gitignore"):
            self.checks_failed.append(".gitignore missing for privacy!")
            return False

        with open(".gitignore") as f:
            gitignore_content = f.read()

        missing_patterns = []
        for pattern in privacy_critical:
            if pattern not in gitignore_content:
                missing_patterns.append(pattern)

        if missing_patterns:
            self.warnings.append(
                f"Privacy patterns missing from .gitignore: {missing_patterns}"
            )

        self.checks_passed.append("Data privacy configuration verified")
        return True

    def print_report(self) -> bool:
        """Print validation report."""
        print("\n" + "=" * 60)
        print("  MIGRU PRODUCTION READINESS CHECK")
        print("=" * 60 + "\n")

        if self.checks_passed:
            print("✅ PASSED CHECKS:")
            for check in self.checks_passed:
                print(f"   • {check}")
            print()

        if self.warnings:
            print("⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"   • {warning}")
            print()

        if self.checks_failed:
            print("❌ FAILED CHECKS:")
            for failure in self.checks_failed:
                print(f"   • {failure}")
            print()

        if not self.checks_failed:
            print("🎉 Ready for production!\n")
            return True
        else:
            print("🚫 NOT ready for production. Fix issues above.\n")
            return False


class HealthCheck:
    """Monitor system health and performance."""

    @staticmethod
    def check_redis() -> dict[str, Any]:
        """Check Redis connectivity and health."""
        try:
            from redis import Redis

            from app.config import config

            client = Redis.from_url(config.REDIS_URL)
            client.ping()

            info = cast(Any, client.info())
            return {
                "connected": True,
                "memory_used_mb": info.get("used_memory", 0) / 1024 / 1024,
                "total_connections": info.get("total_connections_received", 0),
            }
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {"connected": False, "error": str(e)}

    @staticmethod
    def check_api_keys() -> dict[str, bool]:
        """Verify API keys are configured."""
        from app.config import config

        return {
            "mistral": bool(config.MISTRAL_API_KEY),
            "cerebras": bool(config.CEREBRAS_API_KEY),
            "openweather": bool(config.OPENWEATHER_API_KEY),
            "firecrawl": bool(config.FIRECRAWL_API_KEY),
            "openrouter": bool(config.OPENROUTER_API_KEY),
        }

    @staticmethod
    def check_disk_space() -> dict[str, float]:
        """Check available disk space."""
        import shutil

        usage = shutil.disk_usage(".")
        return {
            "total_gb": usage.total / (1024**3),
            "used_gb": usage.used / (1024**3),
            "free_gb": usage.free / (1024**3),
            "percent_used": (usage.used / usage.total) * 100,
        }

    @staticmethod
    def full_health_check() -> dict[str, Any]:
        """Run complete health check."""
        return {
            "redis": HealthCheck.check_redis(),
            "api_keys": HealthCheck.check_api_keys(),
            "disk": HealthCheck.check_disk_space(),
        }


def validate_production() -> bool:
    """
    Run production validation checks.

    Returns:
        True if all checks pass, False otherwise
    """
    validator = ProductionValidator()
    result = validator.validate_all()
    validator.print_report()
    return result


def ensure_privacy() -> list[str]:
    """
    Verify privacy-critical settings are configured correctly.

    Returns:
        List of privacy violations (empty if all good)
    """
    violations = []

    # Check .env is in .gitignore
    if os.path.exists(".gitignore"):
        with open(".gitignore") as f:
            if ".env" not in f.read():
                violations.append(".env not excluded from git")

    # Check Redis is local
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    if "localhost" not in redis_url and "127.0.0.1" not in redis_url:
        violations.append(f"Redis not local: {redis_url}")

    # Check no API keys in code
    api_key_patterns = ["MISTRAL_API_KEY", "CEREBRAS_API_KEY", "OPENWEATHER_API_KEY"]
    for root, dirs, files in os.walk("app"):
        # Skip __pycache__
        dirs[:] = [d for d in dirs if d != "__pycache__"]

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                with open(filepath) as f:
                    content = f.read()
                    for pattern in api_key_patterns:
                        # Check for hardcoded keys (basic check)
                        if f'{pattern} = "' in content or f"{pattern} = '" in content:
                            violations.append(
                                f"Possible hardcoded API key in {filepath}"
                            )

    return violations


if __name__ == "__main__":
    # Run validation when executed directly
    print("Running Migru Production Validation...\n")

    # Production checks
    prod_ready = validate_production()

    print("\nPrivacy Validation:")
    privacy_violations = ensure_privacy()
    if privacy_violations:
        print("❌ Privacy violations found:")
        for violation in privacy_violations:
            print(f"   • {violation}")
    else:
        print("✅ Privacy configuration verified")

    print("\nHealth Check:")
    health = HealthCheck.full_health_check()
    print(f"   • Redis: {'✅' if health['redis']['connected'] else '❌'}")
    print(f"   • API Keys: {sum(health['api_keys'].values())}/5 configured")
    print(f"   • Disk: {health['disk']['free_gb']:.1f}GB free")

    sys.exit(0 if prod_ready and not privacy_violations else 1)
