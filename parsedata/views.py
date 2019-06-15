from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.transaction import atomic
from .models import UserPurchase
from validators.parsedata_validator import clean_data


@atomic
@csrf_exempt
@require_http_methods(["POST"])
def file_parser(request):
    # TODO: restrict file size

    base_teste_file = request.FILES['base_teste']

    response_json = {
        'wrong_column_count': 0,
        'invalid_cpf_count': 0,
        'invalid_loja_mais_frequente': 0,
        'invalid_loja_ultima_compra': 0
    }

    cleaned_data = []

    for i, row in enumerate(base_teste_file):
        if i == 0:
            continue

        row = row.split()

        if len(row) != 8:
            response_json['wrong_column_count'] += 1
            continue

        user_purchase = UserPurchase(**clean_data(row))
        cleaned_data.append(user_purchase)

    try:
        UserPurchase.objects.bulk_create(cleaned_data)
    except IntegrityError as e:
        response_json = {'error': e.args[0]}

    return JsonResponse(response_json)
