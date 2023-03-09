FROM python:3.9

WORKDIR /app

RUN apt update && apt upgrade -y && apt install -y cron python3-pip

COPY . .

# RUN crontab -l | { cat; echo "*/5 * * * * 'python /app/start.py'"; } | crontab -

RUN pip install -r requirements.txt

# ENTRYPOINT ["python", "bot.py"]
RUN touch /tmp/opensquat.log
RUN printenv > /etc/environment
COPY cronjobs /var/spool/cron/crontabs/root
RUN chmod 0644 /var/spool/cron/crontabs/root
RUN crontab /var/spool/cron/crontabs/root

ENTRYPOINT cron && python bot.py