import requests
import config
import logging
import uuid

def generate_shegerpay_link(amount, uid, purpose="PROTOCOL"):
    tx_ref = f"BAYA-{uid}-{purpose}-{uuid.uuid4().hex[:8]}"
    url = "https://api.shegerpay.com/api/v1/payment-links"
    
    headers = {
        "X-API-Key": getattr(config, "SHEGERPAY_API_KEY", ""),
        "Content-Type": "application/json"
    }
    
    payload = {
        "title": f"Baya Books - {purpose}",
        "amount": amount,
        "currency": "ETB",
        "enable_cbe": True,
        "enable_telebirr": True,
        "enable_mpesa": True,
        "enable_crypto": False,
        # Some gateways accept custom reference or metadata
        "reference": tx_ref
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        data = response.json()
        
        # We assume data contains 'url' or 'short_code'
        if response.status_code == 200 or response.status_code == 201:
            short_code = data.get("short_code")
            # ShegerPay URLs usually look like https://shegerpay.com/pay/{short_code}
            checkout_url = data.get("url")
            if not checkout_url and short_code:
                checkout_url = f"https://shegerpay.com/pay/{short_code}"
                
            if checkout_url:
                # We return short_code as tx_ref so we can verify it later via API
                return checkout_url, short_code or tx_ref, None
                
        return None, None, f"ShegerPay Error: {data.get('message', 'Unknown error')}"
    except Exception as e:
        logging.error(f"ShegerPay Init Error: {e}")
        return None, None, f"Network Error: {str(e)}"

def verify_shegerpay_payment(short_code):
    url = f"https://api.shegerpay.com/api/v1/payment-links/{short_code}/status"
    headers = {
        "X-API-Key": getattr(config, "SHEGERPAY_API_KEY", "")
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        if data.get("status") == "verified" or data.get("status") == "approved":
            return True, data
        return False, None
    except Exception as e:
        logging.error(f"ShegerPay Verify Error: {e}")
        return False, None
