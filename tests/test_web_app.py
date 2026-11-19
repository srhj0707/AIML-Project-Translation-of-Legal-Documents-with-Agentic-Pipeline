import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"

def test_sample_endpoint(client):
    res = client.get("/api/sample/bail_order")
    assert res.status_code == 200
    data = res.get_json()
    assert "text" in data
    assert len(data["text"]) > 50

def test_translate_endpoint_json(client):
    sample_text = "The Bail Application is accordingly allowed. Let the Applicant be released on bail."
    res = client.post(
        "/api/translate",
        data=json.dumps({"text": sample_text}),
        content_type="application/json"
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "result" in data
    assert "document_summary" in data["result"]
    assert "translated_document_hindi" in data["result"]
    assert len(data["result"]["clauses"]) >= 1

def test_download_endpoint(client):
    res = client.post(
        "/api/download/text",
        data=json.dumps({"text": "తదనుగుణంగా బెయిల్ దరఖాస్తు మంజూరు చేయబడింది."}),
        content_type="application/json"
    )
    assert res.status_code == 200
    assert "attachment" in res.headers.get("Content-Disposition", "")

def test_translate_endpoint_telugu(client):
    sample_text = "The Bail Application is accordingly allowed. Let the Applicant be released on bail."
    res = client.post(
        "/api/translate",
        data=json.dumps({"text": sample_text, "target_lang": "te"}),
        content_type="application/json"
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["result"]["target_lang_code"] == "te"
    assert "translated_document_telugu" in data["result"]
    assert any('\u0C00' <= char <= '\u0C7F' for char in data["result"]["translated_document"])

def test_translate_endpoint_malayalam(client):
    sample_text = "The Bail Application is accordingly allowed. Let the Applicant be released on bail."
    res = client.post(
        "/api/translate",
        data=json.dumps({"text": sample_text, "target_lang": "ml"}),
        content_type="application/json"
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["result"]["target_lang_code"] == "ml"
    assert "translated_document_malayalam" in data["result"]
    assert any('\u0D00' <= char <= '\u0D7F' for char in data["result"]["translated_document"])

def test_translate_endpoint_tamil(client):
    sample_text = "The Bail Application is accordingly allowed. Let the Applicant be released on bail."
    res = client.post(
        "/api/translate",
        data=json.dumps({"text": sample_text, "target_lang": "ta"}),
        content_type="application/json"
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["result"]["target_lang_code"] == "ta"
    assert "translated_document_tamil" in data["result"]
    assert any('\u0B80' <= char <= '\u0BFF' for char in data["result"]["translated_document"])

def test_translate_endpoint_kannada(client):
    sample_text = "The Bail Application is accordingly allowed. Let the Applicant be released on bail."
    res = client.post(
        "/api/translate",
        data=json.dumps({"text": sample_text, "target_lang": "kn"}),
        content_type="application/json"
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["result"]["target_lang_code"] == "kn"
    assert "translated_document_kannada" in data["result"]
    assert any('\u0C80' <= char <= '\u0CFF' for char in data["result"]["translated_document"])

def test_parse_document_endpoint_txt(client):
    import io
    data = {
        'file': (io.BytesIO(b"The Bail Application is accordingly allowed."), 'petition.txt')
    }
    res = client.post('/api/parse-document', data=data, content_type='multipart/form-data')
    assert res.status_code == 200
    res_data = res.get_json()
    assert res_data["success"] is True
    assert "Bail Application" in res_data["text"]
    assert "Plain Text" in res_data["format"]

def test_parse_document_endpoint_docx(client):
    import io
    import docx
    d = docx.Document()
    d.add_paragraph("The Applicant furnished a bond of Rs. 1,00,000/-.")
    buf = io.BytesIO()
    d.save(buf)
    buf.seek(0)

    data = {
        'file': (buf, 'bail_bond.docx')
    }
    res = client.post('/api/parse-document', data=data, content_type='multipart/form-data')
    assert res.status_code == 200
    res_data = res.get_json()
    assert res_data["success"] is True
    assert "1,00,000" in res_data["text"]
    assert "Word" in res_data["format"]

def test_translate_endpoint_docx_file_upload(client):
    import io
    import docx
    d = docx.Document()
    d.add_paragraph("The Bail Application is accordingly allowed.")
    buf = io.BytesIO()
    d.save(buf)
    buf.seek(0)

    data = {
        'file': (buf, 'order.docx'),
        'target_lang': 'hi'
    }
    res = client.post('/api/translate', data=data, content_type='multipart/form-data')
    assert res.status_code == 200
    res_data = res.get_json()
    assert res_data["success"] is True
    assert "translated_document" in res_data["result"]
    assert any('\u0900' <= char <= '\u097F' for char in res_data["result"]["translated_document"])


