# BotGPT - AI-Powered Chat & Document Q&A Platform

A FastAPI-based conversational AI platform that supports both open chat and document-based question answering using RAG (Retrieval Augmented Generation). Built with async architecture, PostgreSQL, ChromaDB vector store, and multiple LLM providers.

## Features

- 🤖 **Multi-LLM Support**: OpenAI, Groq, and Gemini integration
- 💬 **Streaming Chat**: Real-time token streaming responses
- 📄 **Document Q&A**: Upload PDFs and chat with your documents using RAG
- 🔐 **User Authentication**: JWT-based secure authentication
- 🗄️ **Vector Search**: ChromaDB for semantic document search
- 📊 **Conversation Management**: Track conversation history and metadata
- 🧠 **Auto Intent Classification**: LLM automatically classifies user intent on each message
- ⚡ **Async Architecture**: Built with async/await for high performance
- 🐳 **Docker Support**: Easy deployment with Docker

## Tech Stack

- **Language**: Python 3.12
- **Framework**: FastAPI
- **Database**: PostgreSQL + AsyncPG
- **Vector DB**: ChromaDB
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Authentication**: JWT (python-jose)
- **LLM Clients**: OpenAI, Groq, Gemini
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **PDF Processing**: PyPDF2

## Project Structure

```
.
├── alembic/                    # Database migrations
│   ├── versions/              # Migration files
│   └── env.py                 # Alembic environment config
├── api/                       # API routes
│   ├── conversation.py        # Chat & streaming endpoints
│   ├── document.py            # Document upload & management
│   ├── user.py                # Authentication endpoints
│   └── schemas/               # Pydantic models
├── core/
│   └── config.py              # Environment configuration
├── db/
│   ├── base.py                # SQLAlchemy base
│   ├── session.py             # Database session management
│   ├── chroma_client.py       # ChromaDB client
│   └── models/                # SQLAlchemy models
│       ├── user.py
│       ├── conversation.py
│       ├── message.py
│       └── document.py
├── services/
│   ├── llm/                   # LLM client implementations
│   │   ├── base.py           # Base LLM client interface
│   │   ├── factory.py        # LLM client factory
│   │   ├── groq_client.py
│   │   ├── openai_client.py
│   │   └── gemini_client.py
│   └── rag/                   # RAG service
│       ├── embeddings.py     # Text embedding functions
│       └── rag_service.py    # Document chunking & retrieval
├── utils/
│   ├── auth_helper.py         # JWT helper functions
│   ├── classify_intent.py     # Intent classification utilities
│   └── memory_helper.py       # Memory management utilities
├── uploads/                   # Local document storage
├── cache/                     # ChromaDB data directory
├── main.py                    # Application entry point
├── requirements.txt
├── Dockerfile
└── .env                       # Environment variables
```

## Prerequisites

- Python 3.12 (3.14 not supported due to onnxruntime)
- PostgreSQL 14+
- Docker & Docker Compose (optional)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd bot-gpt
```

### 2. Create Virtual Environment

```bash
python3.12 -m venv venv
source venv/bin/activate  
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the root directory: Add env variables from `.env.example`

### 5. Database Setup

Start PostgreSQL (if not using Docker):

```bash
# macOS
brew services start postgresql@14

# Linux
sudo systemctl start postgresql
```

Create the database:

```bash
createdb botgpt
```

Run migrations:

```bash
alembic upgrade head
```

### 6. Run the Application

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## Docker Setup

### Using Docker Compose (Recommended)

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database
- BotGPT API server

### Building Docker Image Manually

```bash
docker build -t botgpt .
docker run -p 8000:8000 --env-file .env botgpt
```

## API Usage

### 1. User Registration

```bash
curl -X POST "http://localhost:8000/user/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### 2. User Login

```bash
curl -X POST "http://localhost:8000/user/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "refresh_token": "eyJhbGc...",
  "expires_in": 15,
  "refresh_token_expires_in": 60
}
```

### Refresh token

```bash
curl -X POST "http://localhost:8000/user/token/refresh" \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGci...."
  }'
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 15
}
```

### 3. Create Conversation

```bash
curl -X POST "http://localhost:8000/conversation" \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Chat",
    "conversation_mode": "OPEN_CHAT"
  }'
```

**Conversation Modes:**
- `OPEN_CHAT`: Normal AI chat
- `DOCUMENT_QA`: Question answering based on uploaded documents
- `DOCUMENT_SUMMARY`: Document summarization

### 4. Open Chat (Streaming)

Use **Postman** or **curl** to test streaming:

```bash
curl -X POST "http://localhost:8000/conversation/{conversation_id}/messages/stream" \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! How can you help me?"
  }' \
  --no-buffer
```

**Note**: Swagger UI doesn't support streaming. Use Postman or curl for testing.

### 5. Upload Documents (for Document Q&A)

```bash
curl -X POST "http://localhost:8000/document/upload" \
  -H "Authorization: Bearer <your-token>" \
  -F "files=@document.pdf" \
  -F "files=@another.pdf" \
  -F "conversation_id=<conversation-id>"
```

Documents are:
1. Uploaded to `./uploads/` directory
2. Processed in background (text extraction, chunking)
3. Embedded and stored in ChromaDB
4. Status updated to `COMPLETED`

### 6. Chat with Documents

Create a conversation with `DOCUMENT_QA` mode and upload documents first:

```bash
curl -X POST "http://localhost:8000/conversation/{conversation_id}/messages/stream" \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the main topic of the document?"
  }' \
  --no-buffer
```

The system will:
1. Retrieve relevant chunks from uploaded documents
2. Use RAG to answer based on document context
3. Stream the response back

### 7. List Conversations (with Pagination)

```bash
curl -X GET "http://localhost:8000/conversation?page=1&limit=10" \
  -H "Authorization: Bearer <your-token>"
```

### 8. Get Conversation Details (with Paginated Messages)

```bash
curl -X GET "http://localhost:8000/conversation/{conversation_id}?page=1&limit=50" \
  -H "Authorization: Bearer <your-token>"
```

### 9. Delete Conversation

```bash
curl -X DELETE "http://localhost:8000/conversation/{conversation_id}" \
  -H "Authorization: Bearer <your-token>"
```

## How RAG Works

1. **Document Upload**: User uploads PDF documents
2. **Text Extraction**: PyPDF2 extracts text from PDFs
3. **Chunking**: Text is split into 500-character chunks with 50-char overlap
4. **Embedding**: Each chunk is embedded using `all-MiniLM-L6-v2` model
5. **Storage**: Embeddings stored in ChromaDB with document metadata
6. **Retrieval**: User query is embedded and top-k similar chunks retrieved
7. **Generation**: LLM generates answer using retrieved context

## Database Migrations

Create a new migration:

```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:

```bash
alembic upgrade head
```

Rollback migration:

```bash
alembic downgrade -1
```

## Configuration

### Switching LLM Providers

Edit `.env`:

```env
LLM_PROVIDER=openai  # or groq, gemini
```

### Adjusting LLM Parameters

```env
LLM_TEMPERATURE=0.7      # 0.0 to 1.0 (creativity)
LLM_MAX_TOKENS=1024      # Maximum response length
```


## Testing with Postman

1. **Import Environment**: Create variables for `base_url` and `token`
2. **Login**: Send login request, save token from response
3. **Set Authorization**: Add `Bearer {{token}}` to headers
4. **Test Streaming**: 
   - Disable "Automatically follow redirects"
   - Set high timeout
   - Watch response stream in real-time



## TO Do
- [ ] Add tests
- [ ] Add logging
- [ ] Add caching
- [ ] Add rate limiting