from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from new_brand import create_brands
import csv
import logging
import sys
import os

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
CORS(app)

@app.route('/upload', methods=['POST'])
def upload_file():
    logger.info("Upload endpoint called")
    
    if 'file' not in request.files:
        logger.error("No file part in the request")
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        logger.error("No file selected")
        return jsonify({'error': 'No file selected'}), 400

    logger.info(f"Processing file: {file.filename}")
    
    try:
        # read CSV file
        file_contents = file.stream.read().decode("utf-8")
        logger.debug(f"File contents preview: {file_contents[:200]}...")  # Log first 200 chars
        
        csv_rows = file_contents.splitlines()
        logger.info(f"CSV has {len(csv_rows)} rows including header")
        
        if len(csv_rows) <= 1:
            logger.warning("CSV file appears to be empty or contains only headers")
            return jsonify({'error': 'CSV file appears to be empty'}), 400
        
        # Create a custom CSV reader that trims whitespace from column names
        csv_reader = csv.DictReader(csv_rows)
        fieldnames = [name.strip() for name in csv_reader.fieldnames] if csv_reader.fieldnames else []
        logger.info(f"CSV columns (cleaned): {fieldnames}")
        
        # Check for required columns
        required_columns = ['brand_name', 'companyName', 'mainContactName', 'vendorMainContactEmail']
        missing_columns = [col for col in required_columns if col not in fieldnames]
        
        if missing_columns:
            missing_cols_str = ', '.join(missing_columns)
            logger.error(f"CSV is missing required columns: {missing_cols_str}")
            return jsonify({'error': f'CSV file is missing required columns: {missing_cols_str}'}), 400
        
        # Create a new reader with the cleaned fieldnames to process rows
        csv_rows_copy = csv_rows.copy()  # Make a copy to not affect the original data
        # Use cleaned fieldnames for the new reader
        clean_reader = csv.DictReader(csv_rows_copy)
        
        # Create a map of original column name to clean column name
        column_map = {}
        for i, name in enumerate(clean_reader.fieldnames):
            column_map[name] = fieldnames[i]
        
        results = []
        row_count = 0

        for row in clean_reader:
            row_count += 1
            # Create a new row with cleaned keys
            clean_row = {}
            for key, value in row.items():
                if key in column_map:
                    clean_key = column_map[key]
                    clean_row[clean_key] = value.strip() if isinstance(value, str) else value
            
            logger.info(f"Processing row {row_count}: {clean_row}")
            
            # Get required values from CSV columns
            brand_name = clean_row.get('brand_name')
            company_name = clean_row.get('companyName')
            main_contact_name = clean_row.get('mainContactName')
            vendor_email = clean_row.get('vendorMainContactEmail')
            
            # Get optional values from CSV columns
            description = clean_row.get('description')
            founded_year = clean_row.get('foundedInYear')
            country = clean_row.get('countryOfOrigin')
            instagram = clean_row.get('instagramUrl')
            website = clean_row.get('websiteUrl')
            phone = clean_row.get('mainContactPhone')
            
            logger.info(f"Extracted required values - brand_name: {brand_name}, company_name: {company_name}, "
                      f"main_contact_name: {main_contact_name}, vendor_email: {vendor_email}")
            
            if any([description, founded_year, country, instagram, website, phone]):
                logger.info(f"Extracted optional values - description: {description}, founded_year: {founded_year}, "
                          f"country: {country}, instagram: {instagram}, website: {website}, phone: {phone}")

            # Check for missing values in this row
            missing_values = []
            if not brand_name:
                missing_values.append("brand_name")
            if not company_name:
                missing_values.append("companyName")
            if not main_contact_name:
                missing_values.append("mainContactName")
            if not vendor_email:
                missing_values.append("vendorMainContactEmail")
            
            if missing_values:
                missing_values_str = ', '.join(missing_values)
                logger.warning(f"Row {row_count} is missing required values: {missing_values_str}")
                results.append({
                    'brand': brand_name or f"Row {row_count}",
                    'error': f"Missing required values: {missing_values_str}"
                })
                continue

            # Call the API function with the CSV data
            logger.info(f"Calling create_brands for {brand_name}")
            try:
                result = create_brands(
                    brand_name=brand_name, 
                    company_name=company_name, 
                    main_contact_name=main_contact_name, 
                    vendor_email=vendor_email,
                    description=description,
                    founded_year=founded_year,
                    country=country,
                    instagram=instagram,
                    website=website,
                    phone=phone
                )
                
                logger.info(f"create_brands result: {result}")
                
                if isinstance(result, dict) and 'error' in result:
                    results.append({
                        'brand': brand_name,
                        'error': result['error']
                    })
                else:
                    results.append({
                        'brand': brand_name,
                        'result': result
                    })
            except Exception as e:
                logger.error(f"Error in create_brands: {str(e)}")
                results.append({
                    'brand': brand_name,
                    'error': str(e)
                })

        logger.info(f"Upload processing complete. Processed {row_count} rows.")
        return jsonify(results)
    except Exception as e:
        logger.error(f"Exception in upload_file: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

# react static files
@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    logger.info("Starting Flask app")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)