import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from anthropic import Anthropic

app = FastAPI(title="Khabeer AI API")
_client = None

def claude():
    global _client
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise HTTPException(status_code=503,
            detail="أضف ANTHROPIC_API_KEY في Secrets أو Environment Variables للخادم.")
    if _client is None:
        _client = Anthropic(api_key=key)
    return _client

class AskBody(BaseModel):
    question: str

class ExamBody(BaseModel):
    lesson: str
    count: int = 10
    kind: str = "متنوع"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask(body: AskBody):
    response = claude().messages.create(
        model="claude-3-5-haiku-latest", max_tokens=1800,
        system="أنت مساعد تعليمي عربي. أجب بدقة وبأسلوب واضح ومناسب للطلاب.",
        messages=[{"role": "user", "content": body.question}]
    )
    return {"answer": "".join(x.text for x in response.content if hasattr(x, "text"))}

@app.post("/generate-exam")
def generate_exam(body: ExamBody):
    if not body.lesson.strip():
        raise HTTPException(status_code=400, detail="نص الدرس فارغ.")
    response = claude().messages.create(
        model="claude-3-5-haiku-latest", max_tokens=3500,
        system="أنت متخصص في إعداد الاختبارات باللغة العربية. التزم بمحتوى الدرس.",
        messages=[{"role": "user", "content":
            f"أنشئ امتحانًا من الدرس التالي. العدد: {body.count}. النوع: {body.kind}. "
            "رقّم الأسئلة ثم ضع نموذج الإجابة في قسم منفصل. لا تضف معلومات من خارج الدرس.\n\n"
            + body.lesson}]
    )
    return {"exam": "".join(x.text for x in response.content if hasattr(x, "text"))}
