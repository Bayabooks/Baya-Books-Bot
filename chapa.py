import requests
import config
import logging
import uuid

def generate_chapa_link(amount, uid):
    tx_ref = f"BAYA-{uid}-{uuid.uuid4().hex[:8]}"
    url = "https://api.chapa.co/v1/transaction/initialize"
    
    headers = {
        "Authorization": f"Bearer {config.CHAPA_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "amount": str(amount),
        "currency": "ETB",
        "tx_ref": tx_ref,
        "email": f"user{uid}@bayabooks.com",
        "first_name": "Baya",
        "last_name": "Reader",
        "callback_url": f"{config.BASE_URL}/chapa-webhook",
        "return_url": f"{config.BASE_URL}/auto-verify/{tx_ref}",
        "customization": {
            "title": "Baya Books Protocol",
            "description": "Payment for Full Protocol PDF"
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        data = response.json()
        if data.get("status") == "success":
            return data["data"]["checkout_url"], tx_ref
        else:
            logging.error(f"Chapa Init Error: {data}")
            return None, None
    except Exception as e:
        logging.error(f"Chapa Request Error: {e}")
        return None, None

def verify_chapa_payment(tx_ref):
    url = f"https://api.chapa.co/v1/transaction/verify/{tx_ref}"
    headers = {
        "Authorization": f"Bearer {config.CHAPA_SECRET_KEY}"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        if data.get("status") == "success":
            return True, data["data"]
        return False, None
    except Exception as e:
        logging.error(f"Chapa Verify Error: {e}")
        return False, None
