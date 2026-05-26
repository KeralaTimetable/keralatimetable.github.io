import os
import json
import firebase_admin
from firebase_admin import credentials, messaging, db

print("Starting Push Notification Test from GitHub Actions...")

firebase_creds_json = os.environ.get('FIREBASE_CREDENTIALS')

if not firebase_creds_json:
    print("❌ ERROR: FIREBASE_CREDENTIALS secret not found in environment variables!")
    exit(1)

try:
    print("1. Authenticating with Firebase...")
    cred_dict = json.loads(firebase_creds_json)
    cred = credentials.Certificate(cred_dict)
    
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://kerala-timetable-db-default-rtdb.asia-southeast1.firebasedatabase.app'
    })

    print("2. Fetching subscribers from database...")
    ref = db.reference('subscribers')
    subscribers = ref.get()

    if not subscribers:
        print("❌ No subscribers found! Did you click 'Allow' on your website?")
    else:
        tokens = list(subscribers.keys())
        print(f"✅ Found {len(tokens)} subscriber(s). Sending test message...")
        
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title="🚨 KTU Dashboard Test (from GitHub)!",
                body="Your GitHub Actions secret is perfectly wired up!"
            ),
            tokens=tokens
        )
        
        rresponse = messaging.send_each_for_multicast(message)
        print(f"🎯 Push Results -> Success: {response.success_count} | Failed: {response.failure_count}")

except Exception as e:
    print(f"❌ Error: {e}")
