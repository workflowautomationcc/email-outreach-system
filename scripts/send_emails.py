import csv
import smtplib
import time
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

# CONFIG
CSV_FILE = "data/active/leads.csv"
TEMPLATE_FILE = "data/templates/Brokerage_Food_and_Bev.txt"

EMAIL_ADDRESS = "robbie@gtxtransportlogistics.com"
EMAIL_PASSWORD = "gxgr rpjl spnr nuhf"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

EMAILS_PER_RUN = 5
DELAY_SECONDS = 300  # 5 minutes


def load_template():
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    subject_line, body = content.split("\n", 1)
    subject = subject_line.replace("Subject:", "").strip()

    return subject, body


def send_email(to_email, subject, body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)


def main():
    subject, template_body = load_template()

    rows = []

    with open(CSV_FILE, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            rows.append(row)

    sent_count = 0

    for row in rows:
        if sent_count >= EMAILS_PER_RUN:
            break

        if row["outreach_status"] != "sent":

            first_name = row["First Name"]
            company = row["Company Name"]
            email = row["Email Address"]

            body = template_body.replace("{First Name}", first_name)
            body = body.replace("{Company Name}", company)

            print(f"Sending email to {email}")

            send_email(email, subject, body)

            row["outreach_status"] = "sent"
            row["date_sent"] = datetime.now().isoformat()

            sent_count += 1

            if sent_count < EMAILS_PER_RUN:
                time.sleep(DELAY_SECONDS)

    with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()