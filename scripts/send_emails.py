import csv
import smtplib
import time
from datetime import datetime
from email.message import EmailMessage

# CONFIG
CSV_FILE = "data/active/leads.csv"
TEMPLATE_FILE = "data/templates/Brokerage_Food_and_Bev.txt"

EMAIL_ADDRESS = "robbie@gtxtransportlogistics.com"
EMAIL_PASSWORD = "gxgr rpjl spnr nuhf"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

EMAILS_PER_RUN = 5
DELAY_SECONDS = 60

RETRY_LIMIT = 5
RETRY_DELAY = 60

ALERT_EMAIL = "robbie@gtxtransportlogistics.com"


def load_template():
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    subject_line, body = content.split("\n", 1)
    subject = subject_line.replace("Subject:", "").strip()

    return subject, body


def save_csv(rows, email, timestamp):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"CSV update → outreach_status='sent', date_sent='{timestamp}' for {email}")


def send_alert(message):
    try:
        msg = EmailMessage()
        msg["Subject"] = "Email Outreach Script Error"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = ALERT_EMAIL
        msg.set_content(message)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

    except Exception as e:
        print(f"Failed to send alert email: {e}")


def send_email_with_retry(to_email, subject, body):

    for attempt in range(1, RETRY_LIMIT + 1):

        try:

            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = EMAIL_ADDRESS
            msg["To"] = to_email
            msg.set_content(body)

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
                smtp.starttls()
                smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                smtp.send_message(msg)

            return True

        except Exception as e:

            print(f"Attempt {attempt}/{RETRY_LIMIT} failed: {e}")

            if attempt < RETRY_LIMIT:
                print(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                print("All retries failed.")
                send_alert(f"Failed to send email to {to_email}. Error: {e}")
                return False


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

            email = row["Email Address"]
            first_name = row["First Name"]
            company = row["Company Name"]

            body = template_body.replace("{First Name}", first_name)
            body = body.replace("{Company Name}", company)

            print(f"[{sent_count+1}/{EMAILS_PER_RUN}] Sending email to {email}")

            success = send_email_with_retry(email, subject, body)

            if success:

                timestamp = datetime.now().isoformat()

                print(f"[{sent_count+1}/{EMAILS_PER_RUN}] Email successfully sent to {email}")

                row["outreach_status"] = "sent"
                row["date_sent"] = timestamp

                save_csv(rows, email, timestamp)

                sent_count += 1

                if sent_count < EMAILS_PER_RUN:

                    print("Waiting 60 seconds before next email...\n")

                    time.sleep(DELAY_SECONDS)

            else:

                print(f"Skipping {email} due to repeated failure")

    print(f"\nRun finished → {sent_count} emails sent")


if __name__ == "__main__":
    main()