from geopy.distance import geodesic

def calculate_distance(
    user_lat,
    user_lon,
    job_lat,
    job_lon
):

    user_location = (
        user_lat,
        user_lon
    )

    job_location = (
        job_lat,
        job_lon
    )

    distance = geodesic(
        user_location,
        job_location
    ).km

    return round(distance, 2)