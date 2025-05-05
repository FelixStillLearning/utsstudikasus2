from flask import Blueprint, request, jsonify
from app.crypto.aes import encrypt_data, decrypt_data
from app.data.repositories import HealthDataRepository

api_bp = Blueprint('api', __name__)

# Delayed import of db to avoid circular import
repository = None

def set_repository(repo):
    global repository
    repository = repo

@api_bp.route('/healthdata', methods=['POST'])
def add_health_data():
    data = request.json
    encrypted_data = encrypt_data(data['health_info'])
    repository.save_health_data(encrypted_data)
    return jsonify({"message": "Health data added successfully."}), 201

@api_bp.route('/healthdata/<int:data_id>', methods=['GET'])
def get_health_data(data_id):
    encrypted_data = repository.get_health_data(data_id)
    if encrypted_data:
        decrypted_data = decrypt_data(encrypted_data)
        return jsonify({"health_info": decrypted_data}), 200
    return jsonify({"message": "Data not found."}), 404

@api_bp.route('/healthdata/<int:data_id>', methods=['DELETE'])
def delete_health_data(data_id):
    success = repository.delete_health_data(data_id)
    if success:
        return jsonify({"message": "Health data deleted successfully."}), 200
    return jsonify({"message": "Data not found."}), 404