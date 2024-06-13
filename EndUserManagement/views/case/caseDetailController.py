import traceback
import logging
import json

from EndUserManagement.models import Case
from UNHCR_Backend.services import (
    PaginationService,
    TranslationService,
)
from EndUserManagement.serializers.inputValidators import CaseUpdateValidator
from EndUserManagement.serializers.responseSerializers import CaseGetResponseSerializer

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create instances of services
paginationService = PaginationService()
translationService = TranslationService()

# Create your views here.
@api_view(["GET", "PUT", "DELETE"])
def caseDetailController(request, id, **kwargs):
    # loggedUser detected in UNHCR_Backend.middlewares.authMiddleware
    user = kwargs["loggedUser"]
    try:
        case = Case.objects.get(ID=id)
        # The case for uesr trying to operate on a case which does not belong to him/her
        if user.ID != case.User.ID:
            return Response(
                    {"success": False, "message": translationService.translate("HTTP.not.authorized")},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
    except Case.DoesNotExist as err:
        logger.error(traceback.format_exc())
        return Response(
            {"success": False, "message": translationService.translate('case.not.exist')},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == "GET":
        """
        Gets a case.
        @Endpoint: /cases/:id
        """
        try:
            serializer = CaseGetResponseSerializer(case)
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(traceback.format_exc())
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    elif request.method == "PUT":
        """
        Updates a case.
        @Endpoint: /cases/:id
        @BodyParam: Description (String, OPTIONAL)
        """
        try:
            requestBody = request.body.decode('utf-8')
            bodyParams = json.loads(requestBody)
            bodyParamsValidator = CaseUpdateValidator(data = bodyParams)
            isBodyParamsValid = bodyParamsValidator.is_valid(raise_exception = False)
            # The case for body param(s) not being as they should be
            if not isBodyParamsValid:
                return Response(
                    {"success": False, "message": str(bodyParamsValidator.errors)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            validatedData = bodyParamsValidator.validated_data
            for attr, value in validatedData.items():
                setattr(case, attr, value)
            case.save()
            return Response(
                {"success": True, "message": translationService.translate('case.update.successful')},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(traceback.format_exc())
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    elif request.method == "DELETE":
        """
        Deletes a case.
        @Endpoint: /cases/:id
        """
        try:
            case.delete()
            return Response(
                {"success": True, "message": translationService.translate('case.delete.successful')},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(traceback.format_exc())
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    else:
        return Response(
            {"success": False, "message": translationService.translate("HTTP.method.invalid")},
            status=status.HTTP_400_BAD_REQUEST,
        )
