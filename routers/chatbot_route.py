from fastapi import APIRouter, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from services.chat_service import create_chat


templates = Jinja2Templates(directory="templates")

chatbot_router = APIRouter()

@chatbot_router.get("/chatbot", response_class=HTMLResponse)
async def chatbot_page(request: Request):
    request.app.state.medicine_information = getattr(request.app.state, "extra_info_prompt", None)

    return templates.TemplateResponse("chatbot.html", {"request": request})

@chatbot_router.websocket("/ws")
async def web_socket(websocket: WebSocket):
    await websocket.accept()
    
    medicine_information = getattr(websocket.app.state, "medicine_information", None)


    while True:
        try:
            data = await websocket.receive_text()
            print(f"Received message: {data}")
            # Process the message and send response
            await websocket.send_text(f"{create_chat(medicine_information).send_message(message=data).text}")
        except Exception as e:
            print(f"WebSocket error: {e}")
            break