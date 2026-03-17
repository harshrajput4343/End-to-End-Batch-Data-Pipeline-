import boto3
import os
import redshift_connector
from botocore.exceptions import NoCredentialsError

def upload_to_s3(local_file, bucket, s3_file):
    s3 = boto3.client('s3')
    try:
        s3.upload_file(local_file, bucket, s3_file)
        print(f"Upload Successful: {s3_file}")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

def load_s3_to_redshift(bucket, s3_file, table_name):
    # This involves a COPY command which is the AWS best practice
    conn = redshift_connector.connect(
        host=os.getenv('REDSHIFT_HOST'),
        database=os.getenv('REDSHIFT_DB'),
        user=os.getenv('REDSHIFT_USER'),
        password=os.getenv('REDSHIFT_PASSWORD')
    )
    
    cursor = conn.cursor()
    
    copy_query = f"""
    COPY {table_name}
    FROM 's3://{bucket}/{s3_file}'
    IAM_ROLE '{os.getenv('REDSHIFT_IAM_ROLE')}'
    FORMAT AS CSV
    IGNOREHEADER 1;
    """
    
    try:
        cursor.execute(copy_query)
        conn.commit()
        print(f"Successfully loaded {s3_file} into {table_name}")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CLEANED_CSV = os.path.join(PROJECT_ROOT, 'data', 'cleaned_events.csv')
    
    # AWS Specifics
    BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'my-data-bucket')
    S3_KEY = 'ingested/cleaned_events.csv'
    TABLE_NAME = 'raw_data.events'
    
    if os.path.exists(CLEANED_CSV):
        print("Starting AWS Load Process...")
        # upload_to_s3(CLEANED_CSV, BUCKET_NAME, S3_KEY)
        # load_s3_to_redshift(BUCKET_NAME, S3_KEY, TABLE_NAME)
        print("Bypassing actual AWS upload (simulated project template).")
    else:
        print("Run ingest.py first.")
