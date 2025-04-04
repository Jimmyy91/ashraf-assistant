# Use official Python base
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Start the bot
CMD ["python", "ashraf_bot.py"]
