FROM rasa/rasa-sdk:2.0.0

COPY /actions/actions.py /app/actions.py


USER root
RUN pip install --no-cache-dir mysql-connector-python dateparser

USER 1001
CMD ["start", "--actions", "actions"]


