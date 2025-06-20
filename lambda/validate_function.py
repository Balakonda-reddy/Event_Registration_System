import json
import os
import boto3
import mysql.connector
import openai
from datetime import datetime

# Initialize AWS clients
ses_client = boto3.client('ses',
    region_name=os.environ['AWS_REGION']
)

# Initialize OpenAI
openai.api_key = os.environ['OPENAI_API_KEY']

# Database configuration
db_config = {
    'host': os.environ['DB_HOST'],
    'user': os.environ['DB_USER'],
    'password': os.environ['DB_PASSWORD'],
    'database': os.environ['DB_NAME']
}

def get_db_connection():
    return mysql.connector.connect(**db_config)


def analyze_application(registration_data):
    prompt = f"""
    You are an event registration validator. 
    The rules are:
    - If the designation is 'DevOps Engineer' or 'Cloud Engineer' and IT experience is 2 or more years, the seat is confirmed.
    - Otherwise, the seat is not confirmed.

    Analyze the following registration and decide if the seat should be confirmed or not. 
    Respond with ONLY 'ACCEPT' or 'REJECT'.

    Name: {registration_data['name']}
    Designation: {registration_data['designation']}
    IT Experience: {registration_data['it_experience']}
    """

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an event registration validator. Respond with only 'ACCEPT' or 'REJECT'."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def send_email(email, name, decision):
    subject = "Event Registration Decision"
    body = f"""
    Dear {name},

    Thank you for registering for our event. After reviewing your application, we have made the following decision:

    Your registration has been {decision}ED.

    Best regards,
    Event Team
    """
    try:
        # Log the email attempt
        print(f"Attempting to send email to: {email}")
        print(f"Using sender email: {os.environ['SENDER_EMAIL']}")
        
        response = ses_client.send_email(
            Source=os.environ['SENDER_EMAIL'],
            Destination={
                'ToAddresses': [email]
            },
            Message={
                'Subject': {
                    'Data': subject
                },
                'Body': {
                    'Text': {
                        'Data': body
                    }
                }
            }
        )
        print(f"Email sent successfully. MessageId: {response['MessageId']}")
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        print(f"Error details: {type(e).__name__}")
        return False

def lambda_handler(event, context):
    try:
        # Parse the event data
        registration_data = event

        # Analyze the application
        decision = analyze_application(registration_data)

        # Update database with decision
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get the registration ID for this email
        cursor.execute("SELECT id FROM registrations WHERE email = %s", (registration_data['email'],))
        result = cursor.fetchone()
        if not result:
            raise Exception(f"No registration found for email: {registration_data['email']}")
        
        registration_id = result[0]
        
        # Send email
        email_sent = send_email(
            registration_data['email'],
            registration_data['name'],
            decision
        )

        # Update the database
        update_query = """
        UPDATE registrations 
        SET status = %s, 
            llm_decision = %s,
            email_sent = %s
        WHERE id = %s
        """
        cursor.execute(update_query, (
            'ACCEPTED' if 'ACCEPT' in decision.upper() else 'REJECTED',
            decision,
            email_sent,
            registration_id
        ))
        conn.commit()
        cursor.close()
        conn.close()

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Registration processed successfully',
                'decision': decision,
                'email_sent': email_sent
            })
        }

    except Exception as e:
        print(f"Error processing registration: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        } 