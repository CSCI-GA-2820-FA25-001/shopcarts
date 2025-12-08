# Image for a NYU Lab development environment
FROM rofrano/nyu-devops-base:su25

# Set up the Python development environment
USER root
WORKDIR /app
COPY Pipfile Pipfile.lock ./
RUN python -m pip install --upgrade pip pipenv && \
    pipenv install --system --dev

# Copy the application contents
COPY wsgi.py .
COPY service/ ./service/

# Switch to a non-root user and set file ownership
USER root
RUN useradd --uid 1001 flask && \
    chown -R flask /app
USER flask

# Expose any ports the app is expecting in the environment
ENV FLASK_APP="wsgi:app"
ENV PORT=8080
EXPOSE $PORT
CMD ["bash", "-c", "sleep 5 && gunicorn --log-level=info wsgi:app"]

ENV GUNICORN_BIND=0.0.0.0:$PORT
ENTRYPOINT ["gunicorn"]
CMD ["--log-level=info", "wsgi:app"]
