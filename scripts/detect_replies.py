import csv
import imaplib
import email
from datetime import datetime, timedelta

# CONFIG
CSV_FILE = "data/active/leads.csv"

EMAIL_ACCOUNT = "robbie@gtxtransportlogistics.com"
EMAIL_PASSWORD = "gxgr rpjl spnr nuhf"

IMAP_SERVER = "imap.gmail.com"

LOOKBACK_HOURS = 24


def load_csv():
    rows = []

    print("Loading CSV file...")

    with open(CSV_FILE, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            rows.append(row)

    print(f"CSV loaded. Rows found: {len(rows)}\n")

    return rows


def save_csv(rows):
    print("Saving updates to CSV...")

    with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print("CSV successfully updated.\n")


def connect_email():
    print("Connecting to Gmail inbox...")

    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    mail.select("inbox")

    print("Connection successful.\n")

    return mail


def extract_body(msg):
    body = ""

    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode(errors="ignore")
                break
    else:
        body = msg.get_payload(decode=True).decode(errors="ignore")

    return body


def main():

    print("Starting reply detection...\n")

    rows = load_csv()

    mail = connect_email()

    date_since = (datetime.now() - timedelta(hours=LOOKBACK_HOURS)).strftime("%d-%b-%Y")

    print("Searching for emails from last 24 hours...\n")

    result, data = mail.search(None, f'(SINCE "{date_since}")')

    email_ids = data[0].split()

    print(f"Emails found in last 24 hours: {len(email_ids)}\n")

    replies_detected = 0

    for email_id in email_ids:

        result, msg_data = mail.fetch(email_id, "(RFC822)")
        raw_email = msg_data[0][1]

        msg = email.message_from_bytes(raw_email)

        sender = email.utils.parseaddr(msg["From"])[1]

        print(f"Checking email from: {sender}")

        body = extract_body(msg)

        for row in rows:

            if row["Email Address"].lower() == sender.lower():

                if row["reply_received"] != "yes":

                    print("Match found in CSV.")
                    print("Updating reply fields...\n")

                    row["reply_received"] = "yes"
                    row["reply_date"] = datetime.now().isoformat()
                    row["reply_text"] = body[:1000]

                    replies_detected += 1

                else:

                    print("Reply already recorded earlier. Skipping.\n")

    if replies_detected > 0:

        save_csv(rows)

    else:

        print("No new replies found. CSV unchanged.\n")

    print(f"Reply detection complete. New replies recorded: {replies_detected}\n")


if __name__ == "__main__":
    main()