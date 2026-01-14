from ninja import NinjaAPI
from ninja.errors import ValidationError

from api_app_payment.api import router as api_app_payment_router

api = NinjaAPI(
    title="API",
    version="1.0.0",
    description="API разделенный по приложениям Django",
    docs_url="/docs/",
    openapi_url="/openapi.json",
)

@api.exception_handler(ValidationError)
def validation_errors(request, exc):
    return api.create_response(
        request,
        {"detail": exc.errors, "code": "validation_error"},
        status=422,
    )

@api.exception_handler(Exception)
def generic_error(request, exc):
    return api.create_response(
        request,
        {"detail": "Внутренняя ошибка сервера", "code": "server_error"},
        status=500,
    )

api.add_router("/payment/", api_app_payment_router)
