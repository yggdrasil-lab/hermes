from fastapi import FastAPI, HTTPException, status
from app.models.schemas import NotificationRequest
from app.services.email_service import EmailService
from botocore.exceptions import ClientError

app = FastAPI(title="Hermes Notification Gateway")

# Initialize services (lazy initialization or global instance)
email_service = EmailService()

@app.post("/notify", status_code=status.HTTP_200_OK)
async def send_notification(request: NotificationRequest):
    if request.channel == "email":
        if not request.subject:
             # Ideally validate this in Pydantic with a validator, but this works for now
             raise HTTPException(status_code=400, detail="Subject is required for email channel")
        
        try:
            response = email_service.send_email(
                recipient=request.recipient,
                subject=request.subject,
                body=request.body
            )
            return {"status": "success", "message_id": response["MessageId"]}
        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    elif request.channel == "discord":
        # Placeholder for future implementation
        return {"status": "skipped", "detail": "Discord channel not yet implemented"}
    
    else:
        # Should be caught by Pydantic validation, but defensive programming
        raise HTTPException(status_code=400, detail="Unsupported channel")

@app.get("/health")
def health_check():
    return {"status": "ok"}
