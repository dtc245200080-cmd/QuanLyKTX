# Kiến trúc KTX-AI

```text
Browser
   |
   v
FastAPI
   |
   +-- JWT/Auth
   |
   +-- REST API
   |     +-- Students
   |     +-- Rooms/Beds
   |     +-- Stay Requests
   |     +-- Contracts
   |     +-- Finance
   |     +-- Complaints
   |     +-- Policies
   |
   +-- RAG Retriever
   |       |
   |       v
   |    SQLite / policies
   |
   +-- AI Service
           |
           v
       OpenAI Responses API
```

### Luồng chatbot

`Question -> Retriever -> Relevant policies -> Context -> AI -> Answer + Sources`

### Luồng gợi ý xếp phòng

`Student criteria -> SQLite rooms/beds -> Candidate rooms -> AI explanation -> Recommendation`

### Luồng tóm tắt phản ánh

`Complaint -> AI summarization -> ai_summary -> Manager review`
