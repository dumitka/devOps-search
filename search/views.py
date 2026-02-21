import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime

ACCOMMODATION_SERVICE_URL = "http://accommodation-service:8000/api/accommodations/"

@api_view(['GET'])
def search_accommodations(request):
    city = request.GET.get("city")
    guests = request.GET.get("guests")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    sort_by = request.GET.get("sort_by")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    amenity = request.GET.get("amenities")

    response = None
    try:
        response = requests.get(ACCOMMODATION_SERVICE_URL, timeout=5)
        response.raise_for_status() # Ovo baca error ako servis nije dostupan
        data = response.json()
    except requests.exceptions.RequestException as e:
        return Response({"error": f"Accommodation service unavailable: {str(e)}"}, status=503)

    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")

            if start >= end:
                return Response(
                    {"error": "end_date must be after start_date"},
                    status=400
                )
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"},
                status=400
            )

    results = []

    for acc in data:
        if city and city.lower() not in acc["location"]["city"].lower():
            continue
        if guests and int(acc["guests"]) < int(guests):
            continue
        if min_price and acc["price_per_night"] < int(min_price):
            continue
        if max_price and acc["price_per_night"] > int(max_price):
            continue

        results.append(acc)

    if amenity:
        results = [
            acc for acc in results
            if amenity.lower() in [a.lower() for a in acc.get("amenities", [])]
        ]
    
    if sort_by == "price":
        results.sort(key=lambda x: x["price_per_night"])

    elif sort_by == "-price":
        results.sort(key=lambda x: x["price_per_night"], reverse=True)

    elif sort_by == "guests":
        results.sort(key=lambda x: x["guests"])

    elif sort_by == "-guests":
        results.sort(key=lambda x: x["guests"], reverse=True)

    return Response(results)