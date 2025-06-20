from flask import Flask, render_template, request, jsonify
import mysql.connector
import os
from dotenv import load_dotenv
import boto3
import json

# Load environment variables
load_dotenv()

app = Flask(__name__, 
            static_folder='../frontend/static',
            template_folder='../frontend/templates')

# Database configuration
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'register_user'),
    'password': os.getenv('DB_PASSWORD', 'secure123'),
    'database': os.getenv('DB_NAME', 'event_registration')
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        # Get form data
        data = {
            'name': request.form['name'],
            'email': request.form['email'],
            'phone_number': request.form['phone_number'],
            'designation': request.form['designation'],
            'it_experience': request.form['it_experience']
        }

        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if email already exists
        cursor.execute("SELECT id FROM registrations WHERE email = %s", (data['email'],))
        if cursor.fetchone():
            return render_template('error.html', message='This email is already registered. Please use a different email address.'), 400

        # Insert registration data
        query = """
        INSERT INTO registrations 
        (name, email, phone_number, designation, it_experience)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data['name'],
            data['email'],
            data['phone_number'],
            data['designation'],
            data['it_experience']
        ))
        
        conn.commit()
        cursor.close()
        conn.close()

        # Trigger Lambda function
        try:
            lambda_client = boto3.client(
                'lambda',
                region_name=os.getenv('AWS_REGION')
            )
            lambda_payload = {
                'name': data['name'],
                'email': data['email'],
                'phone_number': data['phone_number'],
                'designation': data['designation'],
                'it_experience': data['it_experience']
            }
            response = lambda_client.invoke(
                FunctionName=os.getenv('LAMBDA_FUNCTION_NAME', 'validate_registration'),
                InvocationType='RequestResponse',
                Payload=json.dumps(lambda_payload)
            )
            
            # Parse the Lambda response
            response_payload = json.loads(response['Payload'].read())
            response_body = json.loads(response_payload['body'])
            
            if response_payload['statusCode'] != 200:
                return render_template('error.html', message=f'Error in validation: {response_body.get("error", "Unknown error")}')
                
            if not response_body.get('email_sent', False):
                return render_template('error.html', message='Registration successful but email could not be sent. Please contact support.')
        except Exception as lambda_err:
            return render_template('error.html', message=f'Error triggering validation: {lambda_err}')

        return render_template('success.html')

    except mysql.connector.Error as err:
        error_message = str(err)
        if "Duplicate entry" in error_message and "email" in error_message:
            return render_template('error.html', message='This email is already registered. Please use a different email address.'), 400
        return render_template('error.html', message=f'Database error: {error_message}'), 500
    except Exception as e:
        return render_template('error.html', message=f'An error occurred: {str(e)}'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 