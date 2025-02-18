# AskPod

AskPod is a web application that allows users to upload PDF files and generate podcast audio from the content. The application uses a FastAPI backend to process the PDF files and generate audio, and a Next.js frontend to provide a user interface.

## Features

- User authentication (register, login, logout)
- Upload PDF files
- Generate podcast audio from PDF content

## Getting Started

### Prerequisites

- Node.js
- Python 3.12 or higher

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/askpod.git
cd askpod
```

2. Install frontend dependencies:

```bash
cd askpod
npm install
```

3. Install backend dependencies:

```bash
cd app
pip install -r requirements.txt
```

or using uv

```bash
cd app
uv venv askpod
source .venv/bin/activate
uv sync
```

4. Set up the database:

```bash
cd app
python -m backend.init_db
```

### Running the Application

1. Start the FastAPI backend:

```bash
cd app
uvicorn main:app --reload
```

2. Start the Next.js frontend:

```bash
cd askpod
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.

## Project Structure

- `askpod/`: Next.js frontend application
  - `components/`: React components
  - `pages/`: Next.js pages
  - `styles/`: Global styles
  - `public/`: Public assets
- `app/`: FastAPI backend application
  - `backend/`: Backend modules
  - `main.py`: FastAPI entry point
  - `requirements.txt`: Python dependencies
  - `pyproject.toml`: Python project configuration

## API Endpoints

### Authentication

- `POST /register`: Register a new user
- `POST /login`: Login a user
- `GET /users/me`: Get current user details

### PDF Processing

- `POST /upload_pdf`: Upload a PDF file and get parsed text
- `POST /create_transcript`: Create a transcript from a PDF file
- `POST /generate_podcast`: Generate podcast audio from a PDF file

## Environment Variables

Create a `.env` file in the `app` directory and add the following environment variables:

```
SECRET_KEY=your_secret_key
OPENAI_API_KEY=your_openai_api_key
MODEL_NAME=gpt-4o-mini
BASE_URL=https://api.openai.com/v1/chat/completions
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes.

## License

This project is licensed under the MIT License.
