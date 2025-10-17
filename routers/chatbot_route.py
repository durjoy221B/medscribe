
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from services.chat_service import create_chat

templates = Jinja2Templates(directory="templates")
chatbot_router = APIRouter()

class ChatMessage(BaseModel):
    message: str

# POST endpoint for chat messages (replaces websocket)
@chatbot_router.post("/chatbot/message")
async def chat_message(request: Request, chat: ChatMessage):
    medicine_information = getattr(request.app.state, "medicine_information", None)
    try:
        response = create_chat(medicine_information).send_message(message=chat.message).text
        return JSONResponse(content={"response": response})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@chatbot_router.get("/chatbot", response_class=HTMLResponse)
async def chatbot_page(request: Request):
    request.app.state.medicine_information = getattr(request.app.state, "extra_info_prompt", None)

    return templates.TemplateResponse("chatbot.html", {"request": request})

