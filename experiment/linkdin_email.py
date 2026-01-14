import smtplib

sender = "sushenbiswasaga@gmail.com"
password = "fgsdvfmtzcgcgunz"
receiver = "linkedin_support@cs.linkedin.com"

subject = "Submit Your Question [Case: 251015-034469]"
body = """Hi LinkedIn Safety & Recovery Team,

I completed the Persona identity verification a few days ago and wanted to follow up regarding the restoration of my LinkedIn account. Could you please share an update on the current status of my case?

Thank you very much for your time and support.

Best regards,
Sushen Biswas
sushen.biswas.aga@gmail.com
"""


message = f"Subject: {subject}\n\n{body}"

try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, receiver, message)
    server.quit()
    print("✅ Email sent successfully.")
except Exception as e:
    print("❌ Error:", e)
