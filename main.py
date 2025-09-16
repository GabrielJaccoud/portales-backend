import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuração básica
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

@app.route('/')
def index():
    return jsonify({
        "message": "Portales API is running",
        "version": "1.0.0",
        "status": "healthy"
    }), 200

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "message": "Portales API is running"
    }), 200

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    role = data.get('role', 'explorer')
    
    if not email or not password or not name:
        return jsonify({"message": "Missing required fields"}), 400
    
    print(f"Registering user: {name} ({email}) with role {role}")
    return jsonify({
        "message": "User registered successfully",
        "user": {
            "email": email,
            "name": name,
            "role": role
        }
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"message": "Missing email or password"}), 400
    
    # Simular login bem-sucedido para o admin
    if email == "gabrieljaccoud@gmail.com" and password == "Gj1980101225+":
        return jsonify({
            "message": "Login successful",
            "access_token": "dummy_admin_token",
            "user": {
                "email": email,
                "name": "Gabriel Jaccoud",
                "role": "admin"
            }
        }), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@app.route('/api/users/profile', methods=['PUT'])
def update_profile():
    data = request.get_json()
    avatar_url = data.get('avatar_url')
    website_url = data.get('website_url')
    
    print(f"Updating profile with avatar: {avatar_url}, website: {website_url}")
    return jsonify({
        "message": "Profile updated successfully",
        "avatar_url": avatar_url,
        "website_url": website_url
    }), 200

@app.route('/api/portals', methods=['GET'])
def get_portals():
    portals = [
        {"id": 1, "name": "Portal de Exemplo", "description": "Um portal de exemplo", "category": "Tecnologia"},
        {"id": 2, "name": "Portal de Teste", "description": "Um portal de teste", "category": "Educação"}
    ]
    return jsonify({"portals": portals}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

