from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Constants for service URLs
CARS_SERVICE_URL = 'http://cars:8070/api/v1/cars'
RENTALS_SERVICE_URL = 'http://rentals:8060/api/v1/rental'
PAYMENTS_SERVICE_URL = 'http://payments:8050/api/v1/payment'

# Cars servisine yönlendirme yap
@app.route('/api/v1/cars', methods=['GET'])
def get_cars():
    try:
        response = requests.get(CARS_SERVICE_URL, params=request.args)
        response.raise_for_status()

        cars_data = response.json()
        if isinstance(cars_data, dict) and "items" in cars_data:
            cars_data = cars_data["items"]

        if not isinstance(cars_data, list):
            return jsonify({"error": "Unexpected response format from Cars service"}), 500

        response_body = {
            "page": 1,
            "pageSize": len(cars_data),
            "totalElements": len(cars_data),
            "items": cars_data
        }
        return jsonify(response_body), 200

    except requests.RequestException as e:
        print(f"Error in Cars service: {e}")
        return jsonify({"error": "Cars service is unavailable"}), 503
    except Exception as e:
        print(f"Unexpected error in get_cars: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Rentals servisine yönlendirme yap
@app.route('/api/v1/rental', methods=['POST', 'GET'])
def rental():
    try:
        if request.method == 'POST':
            response = requests.post(RENTALS_SERVICE_URL, json=request.json)
        else:
            response = requests.get(RENTALS_SERVICE_URL, params=request.args)
        response.raise_for_status()

        # Yanıt varsa JSON olarak döndür
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        print(f"Error in Rentals service: {e}")
        return jsonify({"error": "Rentals service is unavailable"}), 503
    except Exception as e:
        print(f"Unexpected error in rental: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Belirli bir rental bilgisi için GET ve DELETE işlemleri
@app.route('/api/v1/rental/<rentalUid>', methods=['GET', 'DELETE'])
def rental_detail(rentalUid):
    try:
        if request.method == 'GET':
            response = requests.get(f"{RENTALS_SERVICE_URL}/{rentalUid}")
        elif request.method == 'DELETE':
            response = requests.delete(f"{RENTALS_SERVICE_URL}/{rentalUid}")
        response.raise_for_status()

        # Yanıt varsa JSON döndür, yoksa boş döndür
        return (response.json() if response.content else ''), response.status_code
    except requests.RequestException as e:
        print(f"Error in Rentals service (detail): {e}")
        return jsonify({"error": "Rentals service is unavailable"}), 503
    except Exception as e:
        print(f"Unexpected error in rental_detail: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Rentals servisi için "finish" işlemi
@app.route('/api/v1/rental/<rentalUid>/finish', methods=['POST'])
def rental_finish(rentalUid):
    try:
        response = requests.post(f"{RENTALS_SERVICE_URL}/{rentalUid}/finish")
        response.raise_for_status()

        # Yanıt varsa JSON döndür, yoksa boş döndür
        return (response.json() if response.content else ''), response.status_code
    except requests.RequestException as e:
        print(f"Error in Rentals service (finish): {e}")
        return jsonify({"error": "Rentals service is unavailable"}), 503
    except Exception as e:
        print(f"Unexpected error in rental_finish: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Payments servisine yönlendirme yap
@app.route('/api/v1/payment', methods=['POST', 'GET'])
def payment():
    try:
        if request.method == 'POST':
            response = requests.post(PAYMENTS_SERVICE_URL, json=request.json)
        else:
            response = requests.get(PAYMENTS_SERVICE_URL, params=request.args)
        response.raise_for_status()

        # Yanıt varsa JSON döndür
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        print(f"Error in Payments service: {e}")
        return jsonify({"error": "Payments service is unavailable"}), 503
    except Exception as e:
        print(f"Unexpected error in payment: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Flask uygulamasını çalıştırma
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
