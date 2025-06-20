# AWS Lambda Setup Guide

This guide provides step-by-step instructions for setting up the validation Lambda function for the Event Registration Application.

## 1. Prerequisites

- AWS CLI installed and configured
- Python 3.8 or later
- Virtual environment (recommended)

## 2. Create Lambda Package

```bash
# Create a new directory for Lambda package
mkdir lambda_package
cd lambda_package

# Create virtual environment (for local testing only)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages in virtual environment (for local testing)
pip install boto3
pip install mysql-connector-python
pip install openai

# Create deployment package for Lambda
# This creates the correct folder structure that Lambda expects
mkdir python
pip install --target ./python boto3 mysql-connector-python openai

# Create the deployment zip
cd python
zip -r ../lambda_deployment.zip .  # First zip all dependencies
cd ..
zip -g lambda_deployment.zip validate_function.py  # Then add your Lambda function

# The final structure in lambda_deployment.zip will be:
# lambda_deployment.zip
# ├── python/
# │   ├── boto3/
# │   ├── mysql/
# │   ├── openai/
# │   └── other dependencies...
# └── validate_function.py
```

Note: The first installation in the virtual environment is optional and only needed if you want to test the code locally. The second installation with `--target ./python` is required for creating the Lambda deployment package.

## 3. Create Lambda Function in AWS Console

1. Go to AWS Lambda Console
2. Click "Create function"
3. Choose "Author from scratch"
4. Basic information:
   - Function name: `validate_registration`
   - Runtime: Python 3.8
   - Architecture: x86_64
   - Permissions: Create a new role with basic Lambda permissions

## 4. Configure IAM Role

The Lambda function needs permissions for:
- SES (for sending emails)
- RDS (for database access)
- CloudWatch Logs (for logging)

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ses:SendEmail",
                "ses:SendRawEmail"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
}
```

To update the role:
1. Go to IAM Console
2. Find your Lambda role
3. Add the above policy as inline policy or create a new managed policy

## 5. Configure Environment Variables

Set these environment variables in Lambda:
```
AWS_REGION=your_region_name
DB_HOST=<EC2_PUBLIC_IP>
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=your_db_name
OPENAI_API_KEY=<your_openai_api_key>
SENDER_EMAIL=<your_verified_ses_email>
```

## 6. Upload Lambda Code

1. Go to Lambda function
2. Click "Upload from" → ".zip file"
3. Upload the `lambda_deployment.zip` created earlier
4. Click "Save"

## 7. Configure Basic Settings

1. Memory: 128 MB (minimum)
2. Timeout: 30 seconds
3. VPC: No VPC (unless your RDS is in a VPC)

## 8. Test the Function

Create a test event:
```json
{
  "name": "Test User",
  "email": "test@example.com",
  "phone_number": "1234567890",
  "designation": "DevOps Engineer",
  "it_experience": "2-5 years"
}
```

## 9. Troubleshooting

### Common Issues:

1. Database Connection Issues:
   - Verify DB_HOST is correct
   - Check security group allows Lambda IP
   - Verify database credentials

2. SES Email Issues:
   - Verify sender email in SES
   - Check if in sandbox mode
   - Verify IAM permissions

3. Package Issues:
   - Check if all dependencies are included
   - Verify Python version matches
   - Check file permissions

### Debugging:
```bash
# View CloudWatch logs
aws logs get-log-events --log-group-name /aws/lambda/validate_registration --log-stream-name <stream_name>

# Test locally
python validate_function.py
```


## 10. Update Process

To update the Lambda function:

1. Make code changes
2. Create new deployment package:
```bash
cd python
zip -r ../lambda_deployment.zip .
cd ..
zip -g lambda_deployment.zip validate_function.py
```

3. Upload new package to Lambda
4. Test with sample event
5. Monitor CloudWatch logs

