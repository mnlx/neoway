from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
@csrf_exempt
@require_http_methods(["POST"])
def file_parser(request):
    # TODO: restrict file size

    base_teste_file = request.FILES['base_teste']

    for chunk in base_teste_file.chunks():

        table_rows = chunk.split(b'\n')

        for i, raw_row in enumerate(table_rows):

            if i == 0:
                continue

            row = raw_row.split()

            print(row)

    return HttpResponse('Worked!')
