from flask import Flask, jsonify, request
import psycopg2
import uuid

app = Flask(__name__)

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="postgres",         
            database="payments",      
            user="postgres", 
            password="postgres"
        )
        return conn
    except Exception as e:
        print("Veritabanı bağlantı hatası:", e)
        return None

# Sağlık kontrolü endpoint'i
@app.route('/manage/health', methods=['GET'])
def health_check():
    return jsonify(status="OK"), 200

# Ödeme ekleme endpoint'i (POST)
@app.route('/api/v1/payment', methods=['POST'])
def create_payment():
    data = request.get_json()
    if not data or 'price' not in data:
        return jsonify({"error": "Invalid data"}), 400

    payment_uid = str(uuid.uuid4())
    status = "PAID"  
    price = data['price']
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Veritabanı bağlantısı sağlanamadı"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO payments (paymentUid, status, price)
            VALUES (%s, %s, %s)
            RETURNING paymentUid;
            """,
            (payment_uid, status, price)
        )
        
        new_payment_uid = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "paymentUid": new_payment_uid,
            "status": status,
            "price": price
        }), 201  
    except Exception as e:
        print(f"Payment creation error: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Tüm ödemeleri listeleyen endpoint (GET)
@app.route('/api/v1/payment', methods=['GET'])
def get_payments():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Veritabanı bağlantısı sağlanamadı"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM payments;")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

       
        payments = [
            {
                "paymentUid": row[0],
                "status": row[1],
                "price": row[2]
            }
            for row in rows
        ]

        return jsonify(payments), 200
    except Exception as e:
        print(f"Error fetching payments: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050)
