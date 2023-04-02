FROM python:3.10 AS development
WORKDIR /app/bot
ADD ./requirements.txt .
RUN pip install --user -r requirements.txt
ADD . .
ENV PATH=/root/.local/bin:$PATH
WORKDIR /app/bot/src

FROM python:3.10-slim AS production
WORKDIR /app/bot
ENV PYTHONPATH "/root/.local/lib/python3.10/site-packages:/app"
COPY --from=development /root/.local /root/.local
COPY --from=development /app/bot/src /app/bot/src
COPY --from=development /app/bot/config-sample.toml /app/bot/config.toml
ENV PATH=/root/.local/bin:$PATH
CMD [ "python", "-m", "src.bot" ]