from g4f.client import Client
from fastapi import FastAPI
from pydantic import BaseModel
import re
from typing import List
from duckduckgo_search import DDGS
from fastapi.responses import JSONResponse

app = FastAPI()

#Описание класса вопроса на вход
class QueryRequest(BaseModel):
    query: str
    id: int

#Запрос на овет от openAI
def ask_openai(query: str) -> str:
    client = Client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": query}],
        web_search=False
    )
    return response.choices[0].message.content

#Предаставление ссылок на информацию, не больше 2
def search_duckduckgo(query: str) -> List[str]:
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=2)  
    return [r["href"] for r in results if "itmo" in r["href"]]  

#Серверная часть для запроса через POST
@app.post("/api/request")
async def handle_request(request: QueryRequest):
    query = request.query
    query_id = request.id

    match = re.findall(r"\d+\.\s(.+?)(?:\n|$)", query)
    options = match if match else None

    response_text = ask_openai(query)
    sources = search_duckduckgo(f"site:itmo.ru {query}")  

    selected_answer = None
    if options:
        for i, option in enumerate(options, start=1):
            if option.lower() in response_text.lower():
                selected_answer = i
                break

    response = {
        "id": query_id,
        "answer": selected_answer,
        "reasoning": response_text,
        "sources": sources 
    }

    return JSONResponse(content=response)

# Команда для запуска: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)