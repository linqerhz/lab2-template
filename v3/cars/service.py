from flask import Flask, jsonify, request  # request eklendi
import psycopg2

app = Flask(__name__)  # `_name_` yerine `__name__` düzeltildi.

# Veritabanına bağlanma fonksiyonu
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="postgres",
            database="cars",
            user="postgres", 
            password="postgres"
        )
        return conn
    except Exception as e:
        print("Veritabanı bağlantı hatası:", e)
        return None

# Veritabanından araç listesini döndüren endpoint
@app.route('/api/v1/cars', methods=['GET'])
def get_cars():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Veritabanı bağlantısı sağlanamadı"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cars;")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Veritabanı sorgu hatası:", e)
        return jsonify({"error": "Veritabanı sorgusu sırasında hata oluştu"}), 500

    # JSON formatına dönüştürme
    cars = []
    for row in rows:
        # availability değerini True veya False olarak ayarlayın
        availability_value = row[8] if len(row) > 8 else False
        if isinstance(availability_value, str):
            availability_value = availability_value.lower() == 't'

        car = {
            "carUid": row[1],
            "brand": row[2],
            "model": row[3],
            "registrationNumber": row[4],
            "power": int(row[5]),
            "type": row[7],
            "price": float(row[6]),
            "available": availability_value
        }
        cars.append(car)

    # Testlerin beklediği tam yanıt yapısı
    response_body = {
        "items": cars,
        "page": 1,
        "pageSize": len(cars),
        "totalElements": len(cars)
    }
    return jsonify(response_body), 200

# Availability güncelleme endpoint'i
@app.route('/api/v1/cars/<carUid>/availability', methods=['PATCH'])
def update_car_availability(carUid):
    data = request.get_json()
    if 'available' not in data:
        return jsonify({"error": "Missing 'available' field"}), 400

    availability = data['available']  # True/False değerini doğrudan kullanıyoruz

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection error"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE cars SET availability = %s WHERE car_uid = %s;",
            (availability, carUid)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Car availability updated successfully"}), 200
    except Exception as e:
        print("Veritabanı güncelleme hatası:", e)
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__": 
    app.run(host="0.0.0.0", port=8070)
