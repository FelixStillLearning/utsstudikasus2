from flask import Blueprint, request, jsonify
import logging
import json

api_bp = Blueprint('api', __name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Repository will be set during app initialization
repository = None

def set_repository(repo):
    global repository
    repository = repo
    logger.info("API repository set")

@api_bp.route('/health-data', methods=['POST'])
def add_health_data():
    """Add encrypted health data to the database"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        user_id = data.get('user_id')
        data_type = data.get('data_type', 'medical_record')
        health_info = data.get('health_info')
        
        if not user_id or not health_info:
            return jsonify({"error": "Missing required fields"}), 400
            
        # Repository handles encryption
        data_id = repository.save_health_data(
            user_id=user_id,
            data_type=data_type,
            raw_data=health_info
        )
        
        return jsonify({
            "message": "Health data encrypted and stored successfully",
            "data_id": data_id
        }), 201
        
    except Exception as e:
        logger.error(f"Error adding health data: {str(e)}")
        return jsonify({"error": "Failed to store health data"}), 500

@api_bp.route('/dna-data', methods=['POST'])
def add_dna_data():
    """Add encrypted DNA data to the database"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        user_id = data.get('user_id')
        dna_info = data.get('dna_info')
        data_type = data.get('data_type', 'dna_analysis')
        
        if not user_id or not dna_info:
            return jsonify({"error": "Missing required fields"}), 400
            
        # Repository handles DNA-specific encryption
        data_id = repository.save_dna_data(
            user_id=user_id,
            raw_data=dna_info,
            data_type=data_type
        )
        
        return jsonify({
            "message": "DNA data encrypted and stored successfully",
            "data_id": data_id
        }), 201
        
    except Exception as e:
        logger.error(f"Error adding DNA data: {str(e)}")
        return jsonify({"error": "Failed to store DNA data"}), 500

@api_bp.route('/health-data/<int:data_id>', methods=['GET'])
def get_health_data(data_id):
    """Retrieve and decrypt health data"""
    try:
        # Repository handles decryption
        decrypted_data = repository.get_health_data(data_id)
        
        if not decrypted_data:
            return jsonify({"error": "Data not found"}), 404
            
        return jsonify({
            "data": decrypted_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving health data: {str(e)}")
        return jsonify({"error": "Failed to retrieve health data"}), 500

@api_bp.route('/user/<int:user_id>/health-data', methods=['GET'])
def get_user_health_data(user_id):
    """Get all health data for a specific user"""
    try:
        # Optional filter by data type
        data_type = request.args.get('data_type')
        
        # Repository handles retrieving and decrypting all records
        data = repository.get_user_health_data(user_id, data_type)
        
        return jsonify({
            "user_id": user_id,
            "count": len(data),
            "data": data
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving user health data: {str(e)}")
        return jsonify({"error": "Failed to retrieve user health data"}), 500

@api_bp.route('/health-data/<int:data_id>', methods=['DELETE'])
def delete_health_data(data_id):
    """Delete health data from the database"""
    try:
        success = repository.delete_health_data(data_id)
        
        if not success:
            return jsonify({"error": "Data not found"}), 404
            
        return jsonify({
            "message": "Health data deleted successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting health data: {str(e)}")
        return jsonify({"error": "Failed to delete health data"}), 500