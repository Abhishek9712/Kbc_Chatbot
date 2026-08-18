FROM python:3.11-slim

WORKDIR /app

# Install dependencies first so this layer is cached across code-only changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Hugging Face Spaces (Docker SDK) sends traffic to port 7860 by default
EXPOSE 7860

# Run as a non-root user (recommended by HF Spaces; also avoids permission
# issues writing kbc_response.mp3 at runtime)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "7860"]
