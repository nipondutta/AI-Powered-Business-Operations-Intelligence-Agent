from pathlib import Path
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.config import settings
from app.db import init_db, engine
from app.schemas import ChatRequest, ChatResponse
from app.agent import ask
from app.ingestion import extract_file
from app.rag import rag
from app.customer_intelligence import customer_insights
from app.llm import ollama_available

app=FastAPI(title=settings.app_name,version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])

@app.on_event("startup")
def startup():
    init_db(); Path(settings.upload_dir).mkdir(parents=True,exist_ok=True)

@app.get("/")
def root(): return {"app":settings.app_name,"docs":"/docs"}

@app.get("/health")
def health(): return {"status":"ok","ollama_available":ollama_available()}

@app.get("/api/dashboard/summary")
def dashboard():
    with engine.connect() as c:
        k=c.execute(text("""SELECT COUNT(*) orders,
          COALESCE(SUM(quantity*unit_price*(1-COALESCE(discount,0))),0) revenue,
          COALESCE(SUM(quantity),0) units FROM orders
          WHERE LOWER(status) NOT IN ('cancelled','refunded')""")).mappings().one()
        customers=c.execute(text("SELECT COUNT(*) FROM customers")).scalar_one()
        tickets=c.execute(text("SELECT COUNT(*) FROM tickets")).scalar_one()
        monthly=c.execute(text("""SELECT substr(order_date,1,7) month,
          ROUND(SUM(quantity*unit_price*(1-COALESCE(discount,0))),2) revenue
          FROM orders WHERE LOWER(status) NOT IN ('cancelled','refunded')
          GROUP BY substr(order_date,1,7) ORDER BY month""")).mappings().all()
        top=c.execute(text("""SELECT p.product_name,
          ROUND(SUM(o.quantity*o.unit_price*(1-COALESCE(o.discount,0))),2) revenue
          FROM orders o JOIN products p ON p.product_id=o.product_id
          WHERE LOWER(o.status) NOT IN ('cancelled','refunded')
          GROUP BY p.product_name ORDER BY revenue DESC LIMIT 5""")).mappings().all()
    return {"kpis":{"orders":k["orders"],"revenue":round(float(k["revenue"]),2),"units":k["units"],"customers":customers,"tickets":tickets},
            "monthly_revenue":[dict(x) for x in monthly],"top_products":[dict(x) for x in top],
            "customer_insights":customer_insights()}

@app.post("/api/chat",response_model=ChatResponse)
def chat(req:ChatRequest):
    try:
        r=ask(req.question)
        return ChatResponse(answer=r.get("answer","No answer generated."),intent=r.get("intent","unknown"),
                            sources=r.get("sources",[]),sql=r.get("sql"),data=r.get("data",[]))
    except Exception as e: raise HTTPException(status_code=500,detail=str(e))


@app.post("/api/knowledge/upload")
async def upload(file: UploadFile = File(...)):
    import traceback

    # Validate file extension
    ext = Path(file.filename or "").suffix.lower()

    if ext not in {".pdf", ".txt", ".md", ".csv", ".xlsx"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type."
        )

    # Prepare filename and destination
    name = Path(file.filename).name.replace(" ", "_")
    dest = Path(settings.upload_dir) / name

    # Save uploaded file
    try:
        with dest.open("wb") as out:
            shutil.copyfileobj(file.file, out)

        print("\n========== DOCUMENT UPLOAD ==========")
        print("Filename:", name)

        # Extract document content
        content = extract_file(str(dest))

        print("Extracted content length:", len(content))
        print("Content preview:", content[:500])

        # Index document
        count = rag.add_text(content, name)

        print("Indexed chunks:", count)

        return {
            "filename": name,
            "chunks_indexed": count
        }

    except Exception as e:
        print("\n========== DOCUMENT UPLOAD ERROR ==========")
        traceback.print_exc()

        dest.unlink(missing_ok=True)

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@app.get("/api/knowledge/search")
def search(q:str): return {"results":rag.search(q)}

@app.get("/api/customer/insights")
def customers(): return customer_insights()
