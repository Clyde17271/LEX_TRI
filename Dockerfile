FROM python:3.13-slim

# Security: Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create working directory with proper ownership
WORKDIR /app
RUN chown appuser:appuser /app

# Install Python dependencies as root, then switch to non-root
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source and set ownership
COPY --chown=appuser:appuser . .

# Switch to non-root user for security
USER appuser

# Set the entrypoint to run the LEX TRI runner.  The runner prints a simple diagnostic header and optionally processes arguments.
ENTRYPOINT ["python", "lextri_runner.py"]