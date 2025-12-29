import boto3
from botocore.exceptions import ClientError
from app.core.config import settings

class EmailService:
    def __init__(self):
        self.client = boto3.client(
            "ses",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

    def send_email(self, recipient: str, subject: str, body: str, sender: str = None) -> dict:
        sender = sender or settings.EMAIL_SENDER
        charset = "UTF-8"

        try:
            response = self.client.send_email(
                Destination={
                    "ToAddresses": [
                        recipient,
                    ],
                },
                Message={
                    "Body": {
                        "Text": {
                            "Charset": charset,
                            "Data": body,
                        },
                        # Basic HTML support mirroring text for now
                        "Html": {
                            "Charset": charset,
                            "Data": body.replace("\n", "<br>"), 
                        },
                    },
                    "Subject": {
                        "Charset": charset,
                        "Data": subject or "No Subject",
                    },
                },
                Source=sender,
            )
        except ClientError as e:
            print(f"Error sending email: {e.response['Error']['Message']}")
            raise e
        else:
            return response
