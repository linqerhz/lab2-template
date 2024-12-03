from flask import Flask, request, jsonify
import psycopg2
import requests
import uuid  # UUID oluşturma için
from datetime import datetime

app = Flask(__name__)  # Düzeltme yapıldı (__name__)

# Veritabanına bağlanma fonksiyonu
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="postgres",  # Docker-compose’da tanımlanan veritabanı servis adı
            database="rentals", 
            user="postgres", 
            password="postgres"
        )
        return conn
    except Exception as e:
        print("Veritabanı bağlantı hatası:", e)
        return None

# Yeni bir kiralama oluşturma endpoint'i
@app.route('/api/v1/rental', methods=['POST'])
def create_rental():
    data = request.get_json()
    print("Received data:", data)

    if not data:
        return jsonify({"error": "Invalid data"}), 400

    car_uid = data.get('carUid')
    date_from = data.get('dateFrom')
    date_to = data.get('dateTo')

    if not all([car_uid, date_from, date_to]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        days = (datetime.strptime(date_to, "%Y-%m-%d") - datetime.strptime(date_from, "%Y-%m-%d")).days
        if days <= 0:
            return jsonify({"error": "Invalid date range"}), 400
    except ValueError as e:
        print("Tarih formatı hatası:", e)
        return jsonify({"error": "Invalid date format"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection error"}), 500

    try:
        cursor = conn.cursor()
        rental_uid = str(uuid.uuid4())
        payment_uid = str(uuid.uuid4())
        price = days * 3500

        # Kiralama kaydı oluşturma
        cursor.execute(
            """
            INSERT INTO rental (rental_uid, username, payment_uid, car_uid, date_from, date_to, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'IN_PROGRESS')
            """,
            (rental_uid, "johndoe", payment_uid, car_uid, date_from, date_to)
        )
        conn.commit()

        # Cars servisine availability güncelleme isteği gönder
        try:
            print("Cars servisine availability güncellemesi gönderiliyor...")
            response = requests.patch(
                f"http://cars:8070/api/v1/cars/{car_uid}/availability",
                json={"available": False}
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print("Error updating car availability:", e)
            return jsonify({"error": "Error updating car availability"}), 500

        return jsonify({
            "rentalUid": rental_uid,
            "carUid": car_uid,
            "status": "IN_PROGRESS",
            "dateFrom": date_from,
            "dateTo": date_to,
            "payment": {
                "paymentUid": payment_uid,
                "status": "PAID",
                "price": price
            }
        }), 200
    except Exception as e:
        print(f"Error during rental creation: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        cursor.close()
        conn.close()

# Tüm kiralamaları listeleyen endpoint
@app.route('/api/v1/rental', methods=['GET'])
def get_rentals():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection error"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rental;")
        rentals = cursor.fetchall()
        rentals_list = [
            {
                "rentalUid": rental[1],
                "car": {
                    "carUid": rental[4],
                    "brand": "Mercedes Benz",
                    "model": "GLA 250",
                    "registrationNumber": "ЛО777Х799"
                },
                "status": rental[7],
                "dateFrom": rental[5].strftime("%Y-%m-%d"),
                "dateTo": rental[6].strftime("%Y-%m-%d"),
                "payment": {
                    "paymentUid": rental[3],
                    "status": "PAID",
                    "price": 3500 * ((rental[6] - rental[5]).days)
                }
            }
            for rental in rentals
        ]
        return jsonify(rentals_list), 200
    except Exception as e:
        print("Veritabanı sorgu hatası:", e)
        return jsonify({"error": "Internal server error"}), 500
    finally:
        cursor.close()
        conn.close()

# Belirli bir kiralamanın bilgilerini döndüren endpoint
@app.route('/api/v1/rental/<rentalUid>', methods=['GET'])
def get_rental(rentalUid):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection error"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rental WHERE rental_uid = %s;", (rentalUid,))
        rental = cursor.fetchone()
        if rental is None:
            return jsonify({"error": "Rental not found"}), 404

        rental_info = {
            "rentalUid": rental[1],
            "car": {
                "carUid": rental[4],
                "brand": "Mercedes Benz",
                "model": "GLA 250",
                "registrationNumber": "ЛО777Х799"
            },
            "status": rental[7],
            "dateFrom": rental[5].strftime("%Y-%m-%d"),
            "dateTo": rental[6].strftime("%Y-%m-%d"),
            "payment": {
                "paymentUid": rental[3],
                "status": "PAID",
                "price": 3500 * ((rental[6] - rental[5]).days)
            }
        }
        return jsonify(rental_info), 200
    except Exception as e:
        print("Veritabanı sorgu hatası:", e)
        return jsonify({"error": "Internal server error"}), 500
    finally:
        cursor.close()
        conn.close()

# Kiralamayı iptal eden endpoint
@app.route('/api/v1/rental/<rentalUid>', methods=['DELETE'])
def cancel_rental(rentalUid):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection error"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE rental SET status = 'CANCELED' WHERE rental_uid = %s RETURNING car_uid;", (rentalUid,))
        car_uid = cursor.fetchone()[0]
        conn.commit()

        # Cars servisine availability güncelleme isteği gönder
        try:
            response = requests.patch(
                f"http://cars:8070/api/v1/cars/{car_uid}/availability",
                json={"available": True}
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print("Error updating car availability:", e)
            return jsonify({"error": "Error updating car availability"}), 500

        return '', 204
    except Exception as e:
        print("Veritabanı sorgu hatası:", e)
        return jsonify({"error": "Internal server error"}), 500
    finally:
        cursor.close()
        conn.close()
# Belirli bir kiralamayı tamamlayan endpoint
@app.route('/api/v1/rental/<rentalUid>/finish', methods=['POST'])
def finish_rental(rentalUid):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection error"}), 500

    try:
        cursor = conn.cursor()
        # rental_uid veritabanında mevcut mu kontrol edin
        cursor.execute("SELECT * FROM rental WHERE rental_uid = %s;", (rentalUid,))
        rental = cursor.fetchone()
        if not rental:
            return jsonify({"error": "Rental not found"}), 404

        # Kiralamayı tamamla
        cursor.execute("UPDATE rental SET status = 'FINISHED' WHERE rental_uid = %s;", (rentalUid,))
        conn.commit()
        return '', 204
    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        if cursor:
            cursor.close()
        conn.close()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8060)
