import datetime
import mimetypes
import os
import secrets
import string
import tempfile

from apps.supabase import create_supabase_client

supabase = create_supabase_client()


def generate_access_token(length=16):
    """Generates a secure random access token with the specified length.

    Args:
        length (int): The length of the access token. Default is 16.

    Returns:
        str: The generated access token.
    """
    characters = string.ascii_letters + string.digits
    token = "".join(secrets.choice(characters) for _ in range(length))
    return token


def upload_file_to_storage(file):
    now = datetime.datetime.now()
    current_datetime = now.strftime("%Y_%m_%d_%H_%M_%S")

    # Get file extension from the file name
    file_extension = os.path.splitext(file.name)[1]

    # Detect the content type based on the file extension
    content_type, _ = mimetypes.guess_type(file.name)
    if content_type is None:
        content_type = "application/octet-stream"  # Fallback to a generic binary type

    # Create a temporary file to save the uploaded file content
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(file.read())  # Write file content to the temp file
        tmp_file_path = tmp_file.name  # Get the temp file path

    # Define the storage path with timestamp and extension
    storage_path = f"materials/{current_datetime}{file_extension}"

    # Upload to Supabase with specified content type
    response = supabase.storage.from_("modules").upload(
        file=tmp_file_path,  # Pass the path of the temp file
        path=storage_path,
        file_options={
            "cache-control": "3600",
            "upsert": "false",
            "content-type": content_type,  # Set the content type
        },
    )

    return {
        "response": response,
        "path": storage_path,
        "content_type": content_type,
    }


def generate_signed_url(file_path):
    response = supabase.storage.from_("modules").get_public_url(file_path)
    return response
