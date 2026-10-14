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

import io
import time
from PIL import Image

def optimize_image_for_ocr(file_bytes):
    """
    Compress and resize large receipt screenshots to prevent timeouts
    when uploading to ShegerPay's OCR API.
    """
    if not file_bytes:
        return file_bytes
    try:
        img = Image.open(io.BytesIO(file_bytes))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        max_dim = 1280
        w, h = img.size
        if max(w, h) > max_dim:
            img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
            
        out_buf = io.BytesIO()
        img.save(out_buf, format='JPEG', quality=85, optimize=True)
        return out_buf.getvalue()
    except Exception as e:
        logging.warning(f"Image optimization skipped: {e}")
        return file_bytes

def verify_receipt_image(file_bytes, expected_amount):
    """
    Calls ShegerPay OCR verification endpoint.
    file_bytes is the downloaded photo from Telegram.
    """
    optimized_bytes = optimize_image_for_ocr(file_bytes)
    
    url = "https://api.shegerpay.com/api/v1/verify-image"
    headers = {
        "X-API-Key": getattr(config, "SHEGERPAY_API_KEY", "")
    }
    
    data = {
        "amount": expected_amount
    }
    
    last_err = None
    for attempt in range(2):
        files = {
            "screenshot": ("receipt.jpg", io.BytesIO(optimized_bytes), "image/jpeg")
        }
        try:
            response = requests.post(url, headers=headers, data=data, files=files, timeout=35)
            resp_data = response.json()
            
            is_verified = resp_data.get("verified", resp_data.get("valid", False))
            if is_verified:
                return True, resp_data.get("reference_id", "OCR_SUCCESS"), None
                
            error_msg = resp_data.get("message", "Receipt verification failed. Please ensure the image is clear and the amount matches.")
            return False, None, error_msg
            
        except requests.exceptions.Timeout:
            last_err = "ShegerPay OCR connection timed out. (Read timed out)"
            logging.warning(f"ShegerPay OCR timeout on attempt {attempt + 1}")
            if attempt == 0:
                time.sleep(1)
                continue
            return False, None, last_err
            
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else 500
            if status_code == 400:
                return False, None, "Invalid receipt image or missing transaction details."
            elif status_code == 401:
                return False, None, "ShegerPay API key authorization error."
            else:
                return False, None, f"ShegerPay server error: {status_code}"
                
        except Exception as e:
            logging.error(f"ShegerPay OCR Error (attempt {attempt + 1}): {e}")
            last_err = f"Network Error: {str(e)}"
            if attempt == 0:
                time.sleep(1)
                continue
            return False, None, last_err

    return False, None, last_err or "Verification failed"

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
