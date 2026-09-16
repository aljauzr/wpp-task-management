from typing import Dict, Any


class HealthService:
    """
    Service responsible for application health and status checks.
    Keeps HTTP concepts decoupled from core business logic.
    """

    def check_health(self) -> Dict[str, Any]:
        """
        Evaluate backend operational status.
        Returns a dictionary representing health state.
        """
        return {
            "status": "ok"
        }
