import secrets, math, os

from boto3 import session, resource
from botocore.client import Config
from os import path
from flask import current_app
from uuid import uuid4

from collections import namedtuple
from operator import attrgetter

S3Obj = namedtuple('S3Obj', ['key', 'mtime', 'size', 'ETag'])

# Initiate session
session = session.Session()

cors_configuration = {
    'CORSRules': [{
        'AllowedHeaders': ['Authorization'],
        'AllowedMethods': ['GET', 'PUT'],
        'AllowedOrigins': ['*'],
        'ExposeHeaders': ['GET', 'PUT'],
        'MaxAgeSeconds': 86400
    }]
}

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0 B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])


def get_client():
    """Creates an Boto S3 Client

    Returns:
        Session.Client: The client from session.client
    """    
    return session.client('s3', 
        region_name=current_app.config["S3_REGION"], 
        endpoint_url=current_app.config["S3_ENDPOINT"], 
        aws_secret_access_key=current_app.config["S3_SECRET_KEY"], 
        aws_access_key_id=current_app.config["S3_ACCESS_KEY"]
    )

def get_resource():
    return session.resource('s3', 
        region_name=current_app.config["S3_REGION"], 
        endpoint_url=current_app.config["S3_ENDPOINT"], 
        aws_secret_access_key=current_app.config["S3_SECRET_KEY"], 
        aws_access_key_id=current_app.config["S3_ACCESS_KEY"]
    )

def create_bucket(bucket_name):
    """Creates a new bucket with the provided name

    Args:
        bucket_name (string): The bucket name to use when creating one

    Returns:
        client.create_bucket/Flase: Returns the response from the server after 
            creating the bucket, if it fails, send a False
    """    
    try:
        client = get_client()
        resp = client.create_bucket(Bucket=bucket_name)
        # Set bucket cors config:
        client.put_bucket_cors(Bucket=bucket_name,
                  CORSConfiguration=cors_configuration)
        return resp
    except:
        return False

def delete_bucket(bucket_name):
    try:
        client = get_client()
        resource = get_resource()
        bucket = resource.Bucket(bucket_name)
        # TODO: More than 1000 objects?
        # Delete all objects first, otherwise bucket delete fails
        bucket.objects.all().delete()
        # Now delete bucket:
        return client.delete_bucket(Bucket=bucket_name)
    except:
        return False


def bucket_listing(bucket_name, path="", deli="/"):
    """Gets all the objects in bucket_name with prefix path

    Args:
        bucket_name (string): The bucket name, usually the project uid
        path (string): The prefix to look for, another way to think of it is the path
        deli (string): The delimeter to divide by

    Returns:
        dict obj: containing folders and files
    """    
    try:
        r = get_resource()
        bucket = r.Bucket(bucket_name)
        if path == "/":
            path = ""
        if len(path) > 1 and path[-1] != "/":
            path += "/"
        
        result = bucket.meta.client \
        .list_objects(Bucket=bucket.name, Prefix=path, Delimiter=deli)
        folders = []
        files = []

        for o in result.get('CommonPrefixes', []):
            folders.append(o.get('Prefix', ''))

        for f in result.get('Contents', []):
            if f.get('Key', "") != path:
                files.append(f)

        return {"folders": folders, "files": files}
    except:
        return { "folders": [], "files": [] }

def get_all_listing(bucket_name, path):
    """Gets all the objects in bucket_name with prefix path

    Args:
        bucket_name (string): The bucket name, usually the project uid
        path (string): The prefix to look for, another way to think of it is the path

    Returns:
        client.list_objects_v2/False: Either a json response or False if failed
    """    
    try:
        client = get_client()
        response = client.list_objects_v2(Bucket=bucket_name, Prefix=path)
        for obj in response['Contents']:
            return response
    except:
        return False

def get_bucket_size(bucket_name):
    resp = get_all_listing(bucket_name, '')
    if resp:
        size = 0
        files = resp["Contents"]
        for f in files:
            size += f["Size"]
        return size
    else:
        return 0
        

def upload_file(bucket, location, f, access="public-read", obstruct=False):
    # TODO: Implement a way to optimize images.
    res = get_resource()
    if obstruct:
        new_file_name = secrets.token_hex(nbytes=16)
        ext = f.filename.split('.')[-1]
        new_file_name += '.'+ext
    else:
        new_file_name = f.filename
    
    try:
        if len(location) == 1:
            location = ""
        elif location[-1] != "/" and len(location) > 1:
            location += "/"
        resp = res.Bucket(bucket).put_object(Key=location+new_file_name, Body=f, ACL=access)
        print(resp)
        return "{}/{}{}".format(bucket, location, new_file_name)
    except:
        return False

