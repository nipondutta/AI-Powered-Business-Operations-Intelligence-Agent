from app.rag import HybridRAG

def test_split_nonempty():
    chunks=HybridRAG.split("Business intelligence " * 100,size=100,overlap=20)
    assert len(chunks)>1 and all(chunks)
