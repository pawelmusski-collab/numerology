from .start import router as start_router
from .birthdate import router as birthdate_router
from .booking import router as booking_router
from .ai_chat import router as ai_router
from .compatibility import router as compat_router

__all__ = ["start_router", "birthdate_router", "booking_router", "ai_router", "compat_router"]
