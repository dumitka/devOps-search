import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime

ACCOMMODATION_SERVICE_URL = "http://accommodations-service:8000/api/accommodations/"

@api_view(['GET'])
def search_accommodations(request):
    city = request.GET.get("city")
    guests = request.GET.get("guests")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    try:
        headers = {}
        auth_header = request.headers.get("Authorization")
        if auth_header:
            headers["Authorization"] = auth_header

        response = requests.get(ACCOMMODATION_SERVICE_URL, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        return Response({"error": f"Service unavailable: {str(e)}"}, status=503)

    search_start = None
    search_end = None
    if start_date and end_date:
        try:
            search_start = datetime.strptime(start_date, "%Y-%m-%d").date()
            search_end = datetime.strptime(end_date, "%Y-%m-%d").date()
            if search_start >= search_end:
                return Response({"error": "End date must be after start date"}, status=400)
        except ValueError:
            return Response({"error": "Invalid date format"}, status=400)

    results = []

    for acc in data:
        acc_city = acc.get("location", {}).get("city", "")
        if city and city.lower() not in acc_city.lower():
            continue

        if guests:
            num_guests = int(guests)
            if not (acc.get("min_guests", 0) <= num_guests <= acc.get("max_guests", 999)):
                continue

        if search_start and search_end:
            is_available = False
            for term in acc.get("availabilities", []):
                term_start = datetime.strptime(term["from_date"], "%Y-%m-%d").date()
                term_end = datetime.strptime(term["to_date"], "%Y-%m-%d").date()
                
                if term_start <= search_start and term_end >= search_end:
                    is_available = True
                    acc["current_price"] = term["price"]
                    break
            
            if not is_available:
                continue

        results.append(acc)

    return Response(results)