FROM python:3.10-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code

CMD ["alembic", "upgrade", "head"]
# Set build argument for port
ARG PORT=8000

# Expose the port specified by the build argument
EXPOSE ${PORT}

# Set environment variable for port
ENV PORT=${PORT}

# Run uvicorn when the container launches, using the port from the environment variable
CMD ["sh", "-c", "uvicorn main:app --reload --port=${PORT} --host=0.0.0.0"]