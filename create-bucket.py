import boto3
from botocore.client import Config
import random 
import string

s3 = boto3.client(
    's3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id='rootuser',
    aws_secret_access_key='rootpass123',
    config=Config(signature_version='s3v4'),
    region_name='us-east-1'
)

# Example: Create a new bucket
bucket_name = 'metaflow-test'
already_present_buckets = s3.list_buckets()["Buckets"]
if not any([bucket['Name'] == bucket_name for bucket in already_present_buckets]):
    s3.create_bucket(Bucket=bucket_name)

# create file with random characters

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

random_chars = randomString(4)
with open('test.txt', 'w') as file:
    file.write('test-'+ random_chars)

with open('test.txt', 'rb') as file:
    s3.upload_fileobj(file, bucket_name, f'test-{random_chars}.txt')

# Example: List objects in a bucket
objects = s3.list_objects(Bucket=bucket_name)
for obj in objects['Contents']:
    print(obj['Key'])