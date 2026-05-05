from decimal import Decimal
try:
    from geopy.exc import GeocoderServiceError
    from geopy.geocoders import Nominatim
except Exception:
    GeocoderServiceError = Exception
    Nominatim = None

ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024


def reverse_geocode_coordinates(latitude, longitude):
    city = 'Unknown Location'
    region = ''
    country = ''
    try:
        if Nominatim is None:
            raise GeocoderServiceError('geopy unavailable')
        geolocator = Nominatim(user_agent='marketflow_africa_dev')
        location = geolocator.reverse(f'{latitude}, {longitude}', language='en', exactly_one=True)
        if location and location.raw:
            address = location.raw.get('address', {})
            city = (
                address.get('city')
                or address.get('town')
                or address.get('village')
                or address.get('municipality')
                or address.get('suburb')
                or address.get('hamlet')
                or address.get('county')
                or city
            )
            region = address.get('state') or address.get('region') or ''
            country = address.get('country') or ''
    except (GeocoderServiceError, ValueError, TypeError):
        pass
    return {
        'city': city,
        'region': region,
        'country': country,
        'latitude': Decimal(str(latitude)).quantize(Decimal('0.000001')),
        'longitude': Decimal(str(longitude)).quantize(Decimal('0.000001')),
    }


def validate_image_upload(file_obj):
    if not file_obj:
        return None
    filename = file_obj.name.lower()
    extension = f".{filename.rsplit('.', 1)[-1]}" if '.' in filename else ''
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        return 'Invalid image type. Upload JPG, JPEG, PNG, or WEBP files.'
    if file_obj.size > MAX_IMAGE_SIZE_BYTES:
        return 'Image is too large. Maximum allowed size is 5MB.'
    return None


def _safe_name(filename):
    return filename.replace(' ', '_')

# path helpers ...
def seller_product_image_path(instance, filename): return f"sellers/product_images/seller_{instance.seller_id or 'unknown'}/{_safe_name(filename)}"
def seller_profile_image_path(instance, filename): return f"sellers/profile_images/user_{instance.user_id or 'unknown'}/{_safe_name(filename)}"
def seller_store_image_path(instance, filename): return f"sellers/store_images/user_{instance.user_id or 'unknown'}/{_safe_name(filename)}"
def buyer_profile_image_path(instance, filename): return f"buyers/profile_images/user_{instance.user_id or 'unknown'}/{_safe_name(filename)}"
def driver_profile_image_path(instance, filename): return f"drivers/profile_images/user_{instance.user_id or 'unknown'}/{_safe_name(filename)}"
def qa_profile_image_path(instance, filename): return f"qa/profile_images/user_{instance.user_id or 'unknown'}/{_safe_name(filename)}"
def admin_profile_image_path(instance, filename): return f"admin/profile_images/user_{instance.user_id or 'unknown'}/{_safe_name(filename)}"
def review_image_path(instance, filename): return f"reviews/buyer_reviews/review_{instance.reviewer_id or 'unknown'}/{_safe_name(filename)}"
def delivery_proof_image_path(instance, filename): return f"drivers/delivery_proofs/order_{instance.order_id or 'unknown'}/{_safe_name(filename)}"
def qa_inspection_image_path(instance, filename): return f"qa/inspection_images/order_{instance.order_id or 'unknown'}/{_safe_name(filename)}"

def profile_image_upload_path(instance, filename):
    return {
        'SELLER': seller_profile_image_path,
        'DRIVER': driver_profile_image_path,
        'QA': qa_profile_image_path,
        'ADMIN_STAFF': admin_profile_image_path,
    }.get(instance.role, buyer_profile_image_path)(instance, filename)
