import boto3
from metaflow._vendor import click
from botocore.client import Config
import random
import string


def randomString(stringLength=10):
    """Generate a random string of fixed length"""
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(stringLength))


@click.command()
@click.option("--access-key", required=True)
@click.option("--secret-key", required=True)
@click.option("--bucket-name", default="metaflow-test")
@click.option("--endpoint-url", default="http://localhost:9000")
def main(access_key, secret_key, bucket_name, endpoint_url):
    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )

    # Example: Create a new bucket
    already_present_buckets = s3.list_buckets()["Buckets"]
    if not any([bucket["Name"] == bucket_name for bucket in already_present_buckets]):
        s3.create_bucket(Bucket=bucket_name)
        click.secho(
            f"Bucket {bucket_name} created successfully.", fg="green", bold=True
        )
    else:
        click.secho(
            f"Bucket {bucket_name} already present. Skipping creation.", fg="yellow"
        )

    # create file with random characters
    random_chars = randomString(4)
    with open("test.txt", "w") as file:
        file.write("test-" + random_chars)

    with open("test.txt", "rb") as file:
        s3.upload_fileobj(file, bucket_name, f"test-{random_chars}.txt")

    # Example: List objects in a bucket
    objects = s3.list_objects(Bucket=bucket_name)
    for obj in objects["Contents"]:
        print(obj["Key"])


if __name__ == "__main__":
    main()