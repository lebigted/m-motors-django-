import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger('mmotors')


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        logger.error(
            f'UNHANDLED_ERROR | view={context["view"].__class__.__name__} | error={str(exc)}',
            exc_info=True,
        )
        return Response(
            {'detail': 'Une erreur interne est survenue. Notre équipe a été alertée.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if response.status_code >= 400:
        logger.warning(
            f'API_ERROR | status={response.status_code} | '
            f'view={context["view"].__class__.__name__} | data={response.data}'
        )

    return response
