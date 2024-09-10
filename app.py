from flask import Flask, request, jsonify, redirect, url_for, render_template
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mySqlR8Pa66@f',
    'database': 'web'
}

@app.route('/api/products', methods=['GET'])
def get_products():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(products)

@app.route('/api/products', methods=['POST'])
def add_product():
    try:
        data = request.get_json()
        
        name = data.get('name')
        price = data.get('price')
        description = data.get('description')
        image = data.get('image')
        quantity = data.get('quantity')
        store = data.get('store')

        # Validate all fields, including the 'store' field
        if not all([name, price, description, image, quantity, store]):
            return jsonify({'error': 'Missing data fields'}), 400

        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Insert the new product into the database
        cursor.execute(
            """
            INSERT INTO products (name, price, description, image, quantity, store)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (name, price, description, image, quantity, store)
        )
        conn.commit()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        # Return a success message
        return jsonify({'message': 'Product added successfully!'}), 201

    except mysql.connector.Error as err:
        # Return a MySQL-specific error message
        return jsonify({'error': f"Database error: {str(err)}"}), 500
    except Exception as e:
        # Return a generic error message
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500


@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        if cursor.rowcount == 0:
            return jsonify({'message': 'Product not found.'}), 404
        
        return jsonify({'message': 'Product deleted successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        data = request.get_json()
        name = data.get('name')
        price = data.get('price')
        description = data.get('description')
        image = data.get('image')
        quantity = data.get('quantity')
        store = data.get('store')  # Include the store field

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE products
            SET name = %s, price = %s, description = %s, image = %s, quantity = %s, store = %s
            WHERE id = %s
            """,
            (name, price, description, image, quantity, store, product_id)
        )
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'message': 'Product not found.'}), 404
        
        cursor.close()
        conn.close()

        return jsonify({'message': 'Product updated successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        address = data.get('address')
        country = data.get('country')
        city = data.get('city')
        zipcode = data.get('zipcode')
        word = data.get('word')

        # Check for missing fields
        if not all([username, email, password, address, country, city, zipcode, word]):
            return jsonify({'error': 'All fields are required!'}), 400

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Get the max ID and increment for the new user
        cursor.execute("SELECT MAX(id) FROM users")
        max_id = cursor.fetchone()[0]
        user_id = int(max_id) + 1 if max_id else 10000001

        # Insert the new user into the database
        cursor.execute(
            "INSERT INTO users (id, username, email, password, address, country, city, zipcode, word) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (user_id, username, email, password, address, country, city, zipcode, word)
        )
        conn.commit()

        # Close the connection
        cursor.close()
        conn.close()
        # Return a success response
        return jsonify({'message': 'Signup successful!'}), 200

    except Exception as e:
        print(f"An error occurred: {e}")

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        email = data.get('email')
        password = data.get('password')

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and user['password'] == password:  
            print("log in success")
            return jsonify({'message': 'Login successful!', 'user': {'username': user['username'], 'id': user['id']}}), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        data = request.form
        email = data.get('email')
        word = data.get('word')
        username = data.get('username')

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        if email and word:
            cursor.execute("SELECT * FROM users WHERE email = %s AND word = %s", (email, word))
        elif username:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            return jsonify({'message': 'User found', 'user': user}), 200
        else:
            return jsonify({'error': 'User not found'}), 404

    return render_template('reset_pass.html')

@app.route('/api/users', methods=['GET'])
def get_users():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users)


@app.route('/api/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()

        if cursor.rowcount == 0:
            return jsonify({'message': 'User not found.'}), 404
        
        return jsonify({'message': 'User deleted successfully!'}), 200
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/add_to_cart', methods=['POST'])
def add_to_cart():
    try:
        # Get data from the request
        data = request.get_json()
        user_id = data.get('user_id')
        product_id = data.get('product_id')
        quantity = data.get('quantity')

        # Check for missing fields
        if not all([user_id, product_id, quantity]):
            return jsonify({'error': 'Missing data fields'}), 400

        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Insert the data into the user_cart table
        cursor.execute(
            "INSERT INTO user_cart (user_id, product_id, quantity) VALUES (%s, %s, %s)",
            (user_id, product_id, quantity)
        )
        conn.commit()

        # Close the connection
        cursor.close()
        conn.close()

        # Return a success message
        return jsonify({'message': 'Product added to cart successfully!'}), 201

    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    try:
        print(user_id)
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Get cart items for the given user_id
        cursor.execute("""
            SELECT 
                uc.product_id, 
                p.name, 
                p.description, 
                p.price, 
                p.image, 
                uc.quantity,
                p.store 
            FROM 
                user_cart uc
            JOIN 
                products p ON uc.product_id = p.id
            WHERE 
                uc.user_id = %s
        """, (user_id,))
        
        cart_items = cursor.fetchall()

        # Close the connection
        cursor.close()
        conn.close()
        
        # Return the cart items
        return jsonify(cart_items), 200

    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='', port=5000)
