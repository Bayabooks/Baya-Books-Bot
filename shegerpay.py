import requests
import config
import logging
import uuid
import os

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
        "reference": tx_ref
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        data = response.json()
        
        if response.status_code in (200, 201):
            short_code = data.get("short_code")
            checkout_url = data.get("url")
            if not checkout_url and short_code:
                checkout_url = f"https://shegerpay.com/pay/{short_code}"
                
            if checkout_url:
                return checkout_url, short_code or tx_ref, None
                
        return None, None, f"ShegerPay Error: {data.get('message', 'Unknown error')}"
    except Exception as e:
        logging.error(f"ShegerPay Init Error: {e}")
        return None, None, f"Network Error: {str(e)}"

def verify_receipt_image(file_bytes, expected_amount):
    """
    Calls ShegerPay OCR verification endpoint.
    file_bytes is the downloaded photo from Telegram.
    """
    url = "https://api.shegerpay.com/api/v1/verify-image"
    headers = {
        "X-API-Key": getattr(config, "SHEGERPAY_API_KEY", "")
        # Do not set Content-Type to application/json, requests handles multipart/form-data automatically
    }
    
    # The API expects amount and screenshot
    data = {
        "amount": expected_amount
    }
    
    files = {
        "screenshot": ("receipt.jpg", file_bytes, "image/jpeg")
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, files=files, timeout=20)
        resp_data = response.json()
        
        # Check standard verification response fields: verified/valid
        is_verified = resp_data.get("verified", resp_data.get("valid", False))
        
        if is_verified:
            return True, resp_data.get("reference_id", "OCR_SUCCESS"), None
            
        error_msg = resp_data.get("message", "Receipt verification failed. Please ensure the image is clear and the amount matches.")
        return False, None, error_msg
        
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else 500
        if status_code == 400:
            return False, None, "Invalid receipt image or missing transaction details."
        elif status_code == 401:
            return False, None, "API configuration error."
        else:
            return False, None, f"Server error: {status_code}"
    except Exception as e:
        logging.error(f"ShegerPay OCR Error: {e}")
        return False, None, f"Network Error: {str(e)}"

def verify_shegerpay_payment(short_code):
    url = f"https://api.shegerpay.com/api/v1/payment-links/{short_code}/status"
    headers = {
        "X-API-Key": getattr(config, "SHEGERPAY_API_KEY", "")
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        if data.get("status") in ("verified", "approved", "success", "paid"):
            return True, data
        return False, None
    except Exception as e:
        logging.error(f"ShegerPay Verify Error: {e}")
        return False, None
