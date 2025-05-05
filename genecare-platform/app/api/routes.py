from flask import Blueprint, request, jsonify, current_app
import logging
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required

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
@login_required
def add_health_data():
    """Add encrypted health data to the database"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        user_id = current_user.id
        data_type = data.get('data_type', 'medical_record')
        health_info = data.get('health_info')
        
        if not health_info:
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
@login_required
def add_dna_data():
    """Add encrypted DNA data to the database"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        user_id = current_user.id
        dna_info = data.get('dna_info')
        data_type = data.get('data_type', 'dna_analysis')
        
        if not dna_info:
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
@login_required
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

@api_bp.route('/user/health-data', methods=['GET'])
@login_required
def get_user_health_data():
    """Get all health data for the current user"""
    try:
        user_id = current_user.id
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
@login_required
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

# New API endpoints for DNA upload and recommendations
@api_bp.route('/dna-upload', methods=['POST'])
@login_required
def upload_dna_file():
    """Handle DNA file upload, encrypt and store the data"""
    try:
        if 'dnaFile' not in request.files:
            return jsonify({"error": "No file provided"}), 400
            
        file = request.files['dnaFile']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
            
        # Get form data
        data_type = request.form.get('dataType', 'dna_analysis')
        notes = request.form.get('notes', '')
        
        # Read file content
        file_content = file.read().decode('utf-8')
        
        # Create metadata with original filename and notes
        metadata = {
            'filename': secure_filename(file.filename),
            'upload_date': datetime.now().isoformat(),
            'notes': notes
        }
        
        # Combine data and metadata
        dna_data = {
            'content': file_content,
            'metadata': metadata
        }
        
        # Save with DNA-specific encryption
        data_id = repository.save_dna_data(
            user_id=current_user.id,
            raw_data=json.dumps(dna_data),
            data_type=data_type
        )
        
        return jsonify({
            "message": "DNA data encrypted and stored successfully",
            "data_id": data_id
        }), 201
        
    except Exception as e:
        logger.error(f"Error uploading DNA file: {str(e)}")
        return jsonify({"error": "Failed to process DNA data"}), 500

@api_bp.route('/my-dna-data', methods=['GET'])
@login_required
def get_my_dna_data():
    """Get all DNA data for the current user"""
    try:
        # Get all DNA-related records
        data = repository.get_user_health_data(
            user_id=current_user.id, 
            data_type='dna_analysis'  # Can be expanded to include other DNA types
        )
        
        # Format response data
        formatted_data = []
        for item in data:
            # Parse the decrypted data if it's a JSON string
            if isinstance(item['data'], str):
                try:
                    parsed_data = json.loads(item['data'])
                    # Extract metadata if available
                    metadata = parsed_data.get('metadata', {})
                    date_added = metadata.get('upload_date')
                    if not date_added and hasattr(item.get('created_at'), 'isoformat'):
                        date_added = item['created_at'].isoformat()
                    elif not date_added:
                        date_added = str(item.get('created_at', 'Unknown date'))
                        
                    formatted_data.append({
                        'id': item['id'],
                        'dataType': item['data_type'],
                        'dateAdded': date_added,
                        'filename': metadata.get('filename', 'DNA Data'),
                        'notes': metadata.get('notes', '')
                    })
                except json.JSONDecodeError:
                    # If not JSON, just use the basic info
                    date_added = str(item.get('created_at', 'Unknown date'))
                    if hasattr(item.get('created_at'), 'isoformat'):
                        date_added = item['created_at'].isoformat()
                        
                    formatted_data.append({
                        'id': item['id'],
                        'dataType': item['data_type'],
                        'dateAdded': date_added,
                        'filename': 'DNA Data'
                    })
            else:
                # If already a dictionary
                date_added = str(item.get('created_at', 'Unknown date'))
                if hasattr(item.get('created_at'), 'isoformat'):
                    date_added = item['created_at'].isoformat()
                    
                formatted_data.append({
                    'id': item['id'],
                    'dataType': item['data_type'],
                    'dateAdded': date_added,
                    'filename': 'DNA Data'
                })
        
        return jsonify({
            "data": formatted_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving DNA data: {str(e)}")
        return jsonify({"error": "Failed to retrieve DNA data"}), 500

@api_bp.route('/recommendations', methods=['GET'])
@login_required
def get_recommendations():
    """Get health recommendations based on DNA analysis"""
    try:
        # Optional: Specific DNA data ID
        dna_data_id = request.args.get('data_id')
        
        # For now, return sample recommendations
        # In a real application, this would analyze the encrypted DNA data
        # and generate personalized recommendations
        sample_recommendations = [
            {
                "title": "Cardiovascular Health",
                "category": "Heart Health",
                "description": "Your genetic profile indicates a slightly elevated risk for cardiovascular issues. Regular monitoring of blood pressure and cholesterol is recommended.",
                "riskLevel": "medium"
            },
            {
                "title": "Vitamin D Metabolism",
                "category": "Nutrition",
                "description": "Your genetic variants suggest you may have reduced vitamin D synthesis. Consider supplementation and regular blood tests to monitor levels.",
                "riskLevel": "high"
            },
            {
                "title": "Caffeine Sensitivity",
                "category": "Lifestyle",
                "description": "Your genetic profile suggests you metabolize caffeine slowly. Consider limiting caffeine intake, especially in the afternoon and evening.",
                "riskLevel": "medium"
            },
            {
                "title": "Exercise Response",
                "category": "Fitness",
                "description": "Your genes indicate you may respond well to endurance training. Consider incorporating more cardio exercises in your fitness routine.",
                "riskLevel": "low"
            },
            {
                "title": "Gluten Sensitivity",
                "category": "Nutrition",
                "description": "No genetic markers for celiac disease or gluten sensitivity were detected.",
                "riskLevel": "low"
            },
            {
                "title": "Lactose Tolerance",
                "category": "Nutrition",
                "description": "Your genetic profile suggests you maintain lactase production into adulthood, indicating good tolerance for dairy products.",
                "riskLevel": "low"
            }
        ]
        
        return jsonify({
            "recommendations": sample_recommendations
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        return jsonify({"error": "Failed to generate recommendations"}), 500

# Medical records API endpoints
@api_bp.route('/medical-records', methods=['GET'])
@login_required
def get_medical_records():
    """Get paginated medical records for the current user"""
    try:
        page = int(request.args.get('page', 1))
        record_type = request.args.get('record_type', 'all')
        search = request.args.get('search', '')
        
        per_page = 10
        start_idx = (page - 1) * per_page
        
        # Get all health records (excluding DNA data)
        all_records = repository.get_user_health_data(
            user_id=current_user.id,
            data_type=None if record_type == 'all' else record_type
        )
        
        # Filter out DNA records
        medical_records = [
            record for record in all_records 
            if 'dna' not in record['data_type'].lower()
        ]
        
        # Simple search implementation
        if search:
            search = search.lower()
            medical_records = [
                record for record in medical_records
                if (search in record['data_type'].lower() or
                    (isinstance(record['data'], dict) and
                     search in str(record['data']).lower()))
            ]
        
        # Calculate pagination
        total_records = len(medical_records)
        total_pages = (total_records + per_page - 1) // per_page
        
        # Get current page records
        current_records = medical_records[start_idx:start_idx + per_page]
        
        # Format records for display
        formatted_records = []
        for record in current_records:
            if isinstance(record['data'], str):
                try:
                    data = json.loads(record['data'])
                except json.JSONDecodeError:
                    data = {"title": "Medical Record", "details": record['data']}
            else:
                data = record['data']
            
            # Handle created_at properly
            record_date = data.get('date')
            if not record_date:
                if hasattr(record.get('created_at'), 'isoformat'):
                    record_date = record['created_at'].isoformat()
                else:
                    record_date = str(record.get('created_at', 'Unknown date'))
                
            formatted_records.append({
                "id": record['id'],
                "date": record_date,
                "type": record['data_type'],
                "provider": data.get('provider', 'N/A'),
                "title": data.get('title', 'Medical Record')
            })
        
        return jsonify({
            "records": formatted_records,
            "pagination": {
                "currentPage": page,
                "totalPages": total_pages,
                "totalRecords": total_records,
                "perPage": per_page
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving medical records: {str(e)}")
        return jsonify({"error": "Failed to retrieve medical records"}), 500

@api_bp.route('/medical-records/<int:record_id>', methods=['GET'])
@login_required
def get_medical_record(record_id):
    """Get details of a specific medical record"""
    try:
        # Get and decrypt the record
        record_data = repository.get_health_data(record_id)
        
        if not record_data:
            return jsonify({"error": "Record not found"}), 404
            
        # Convert string to JSON if needed
        if isinstance(record_data, str):
            try:
                record_data = json.loads(record_data)
            except json.JSONDecodeError:
                record_data = {"details": record_data}
        
        return jsonify({
            "record": record_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving medical record details: {str(e)}")
        return jsonify({"error": "Failed to retrieve record details"}), 500

@api_bp.route('/medical-records', methods=['POST'])
@login_required
def add_medical_record():
    """Add a new medical record with encryption"""
    try:
        # Get form data
        record_type = request.form.get('recordType')
        record_date = request.form.get('recordDate')
        provider = request.form.get('providerName')
        title = request.form.get('recordTitle')
        details = request.form.get('recordDetails')
        
        if not record_type or not title:
            return jsonify({"error": "Missing required fields"}), 400
            
        # Handle file attachment if present
        attachments = []
        if 'recordFile' in request.files:
            file = request.files['recordFile']
            if file and file.filename != '':
                # In a real app, save file to secure storage
                # For this demo, we'll just include metadata
                attachments.append({
                    "id": "file1",  # Would be a real ID in production
                    "name": secure_filename(file.filename),
                    "size": len(file.read()),
                    "type": file.content_type
                })
        
        # Create record data structure
        record_data = {
            "type": record_type,
            "date": record_date,
            "provider": provider,
            "title": title,
            "details": details,
            "attachments": attachments
        }
        
        # Save with encryption
        data_id = repository.save_health_data(
            user_id=current_user.id,
            data_type=record_type,
            raw_data=json.dumps(record_data)
        )
        
        return jsonify({
            "message": "Medical record encrypted and saved successfully",
            "record_id": data_id
        }), 201
        
    except Exception as e:
        logger.error(f"Error adding medical record: {str(e)}")
        return jsonify({"error": "Failed to save medical record"}), 500

@api_bp.route('/medical-records/<int:record_id>', methods=['DELETE'])
@login_required
def delete_medical_record(record_id):
    """Delete a medical record"""
    try:
        success = repository.delete_health_data(record_id)
        
        if not success:
            return jsonify({"error": "Record not found"}), 404
            
        return jsonify({
            "message": "Medical record deleted successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting medical record: {str(e)}")
        return jsonify({"error": "Failed to delete medical record"}), 500