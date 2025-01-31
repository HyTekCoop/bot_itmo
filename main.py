from g4f.client import Client
from fastapi import FastAPI
from pydantic import BaseModel
import re


app = FastAPI()

class QueryRequest(BaseModel):
    query: str
    id: int

def ask_openai(query: str) -> str:
    client = Client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": query}],
        web_search=False
    )
    return response.choices[0].message.content


@app.post("/api/request")
async def handle_request(request: QueryRequest):
    query = request.query
    query_id = request.id

    match = re.findall(r"\d+\.\s(.+?)(?:\n|$)", query)
    options = match if match else None

    response = ask_openai(query)

    selected_answer = None
    if options:
        for i, option in enumerate(options, start=1):
            if option.lower() in response.lower():
                selected_answer = i
                break

    response = {
        "id": query_id,
        "answer": selected_answer,
        "reasoning": response,
        "sources": "test"
    }

    return response



# Команда для запуска: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)