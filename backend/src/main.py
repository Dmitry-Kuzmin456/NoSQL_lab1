import uvicorn
from fastapi import FastAPI

from domain.user import UserRole
from infrastructure.http.auth.controller import router as auth_router
from infrastructure.http.auth.dependencies import get_token_service
from infrastructure.http.cart.controller import router as cart_router
from infrastructure.http.checkout.controller import router as checkout_router
from infrastructure.http.exception_handlers import setup_exception_handlers
from infrastructure.http.favourites.controller import router as favourites_router
from infrastructure.http.health.controller import router as health_router
from infrastructure.http.middleware.authentication_middleware import (
    authentication_middleware,
)
from infrastructure.http.middleware.authorization_middleware import (
    RouteAuthRule,
    authorization_middleware,
)
from infrastructure.http.order.controller import router as order_router
from infrastructure.http.product.controller import router as product_router
from infrastructure.http.recovery.controller import router as recovery_router
from infrastructure.http.teacher.controller import router as teacher_router
from infrastructure.http.user.controller import router as user_router

auth_rules: list[RouteAuthRule] = [
    RouteAuthRule.create(
        path="/api/auth/logout-all/{user_id}",
        methods={"POST"},
        allowed_roles=set(UserRole),
    ),
    RouteAuthRule.create(
        path="/api/auth/logout",
        methods={"POST"},
        allowed_roles=set(UserRole),
    ),
    RouteAuthRule.create(
        path="/api/orders/{order_id}/approve",
        methods={"POST"},
        allowed_roles={UserRole.ADMIN},
    ),
    RouteAuthRule.create(
        path="/api/orders/{order_id}/reject",
        methods={"POST"},
        allowed_roles={UserRole.ADMIN},
    ),
    RouteAuthRule.create(
        path="/api/orders",
        allowed_roles=set(UserRole),
    ),
    RouteAuthRule.create(
        path="/api/products",
        methods={"POST", "PATCH", "DELETE"},
        allowed_roles={UserRole.ADMIN},
    ),
    RouteAuthRule.create(
        path="/api/favourites",
        allowed_roles=set(UserRole),
    ),
    RouteAuthRule.create(
        path="/api/cart",
        allowed_roles=set(UserRole),
    ),
    RouteAuthRule.create(
        path="/api/checkout",
        allowed_roles=set(UserRole),
    ),
    RouteAuthRule.create(
        path="/api/users",
        methods={"DELETE"},
        allowed_roles={UserRole.ADMIN},
    ),
    RouteAuthRule.create(
        path="/api/users/{user_id}/change-password",
        methods={"POST"},
        allowed_roles=set(UserRole),
    ),
    RouteAuthRule.create(
        path="/api/users",
        methods={"GET", "PATCH"},
        allowed_roles=set(UserRole),
    ),
    RouteAuthRule.create(
        path="/api/teachers",
        allowed_roles={UserRole.TEACHER},
    ),
]

app = FastAPI(title="Our site")

setup_exception_handlers(app)

app.add_middleware(authorization_middleware(rules=auth_rules))
app.add_middleware(authentication_middleware(token_service=get_token_service()))

app.include_router(health_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(product_router, prefix="/api")
app.include_router(favourites_router, prefix="/api")
app.include_router(cart_router, prefix="/api")
app.include_router(checkout_router, prefix="/api")
app.include_router(teacher_router, prefix="/api")
app.include_router(recovery_router, prefix="/api")
app.include_router(order_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# TODO: Cart application and infrastructure level still need to be finished.
# TODO: Events history application and infrastructure level still need to be finished.
# TODO: Choose db for all domains
# TODO: Implement repositories
