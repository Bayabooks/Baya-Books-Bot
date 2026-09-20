import logging
from io import BytesIO
from PIL import Image
import ethiobank_receipts
from pyzbar.pyzbar import decode

def extract_qr_url(image_bytes):
    try:
        img = Image.open(BytesIO(image_bytes))
        decoded_objects = decode(img)
        for obj in decoded_objects:
            data = obj.data.decode('utf-8')
            if 'http' in data or 'https' in data:
                return data
            # CBE might return just the ID in some QRs, or telebirr might.
            return data
    except Exception as e:
        logging.error(f"QR decode error: {e}")
    return None

def verify_with_ethiobank(text_or_url, expected_amount, expected_name, expected_phone):
    """
    Tries to verify using ethiobank_receipts.
    Returns (True/False (is_approved), tx_id, error_message, dict_of_data)
    """
    if not text_or_url:
        return False, None, "No data provided", None

    try:
        # Determine bank
        if 'cbe' in text_or_url.lower() or 'cbeibe' in text_or_url.lower() or 'combanketh' in text_or_url.lower():
            bank = 'cbe'
        else:
            # Default to telebirr
            bank = 'tele'

        data = ethiobank_receipts.extract_receipt(bank, text_or_url)
        if not data:
            return False, None, "Could not extract data", None

        # Parse data
        tx_id = data.get('reference_no') or data.get('transaction_id')
        if not tx_id and bank == 'tele':
            # telebirr might not return transaction_id in the library directly, we can use the URL/ID as fallback
            tx_id = text_or_url.split('/')[-1] if '/' in text_or_url else text_or_url

        amount_str = str(data.get('transferred_amount') or data.get('total_paid', '0'))
        amount_str = amount_str.replace(',', '').replace(' ETB', '').replace('ETB', '').strip()
        try:
            amount = float(amount_str)
        except:
            amount = 0.0

        receiver = (data.get('receiver') or data.get('credited_party') or "").lower()
        receiver_acc = (data.get('receiver_account') or data.get('credited_party_number') or "").lower()

        # Checks
        if amount < float(expected_amount):
            return False, tx_id, f"Amount is {amount}, expected {expected_amount}", data

        if bank == 'tele':
            # check name or phone
            expected_name_l = expected_name.lower()
            expected_phone_l = expected_phone.lower()
            if expected_name_l not in receiver and expected_phone_l not in receiver_acc and expected_phone_l not in receiver:
                # sometimes names are formatted differently, allow if partial match
                parts = expected_name_l.split()
                if not any(p in receiver for p in parts) and expected_phone_l not in receiver_acc:
                    return False, tx_id, f"Receiver '{receiver}' doesn't match expected '{expected_name}'", data
            
            status = data.get('status', '').lower()
            if status and 'complete' not in status and 'success' not in status:
                 return False, tx_id, f"Status is {status}", data

        elif bank == 'cbe':
            # verify CBE
            expected_name_l = expected_name.lower()
            parts = expected_name_l.split()
            if not any(p in receiver for p in parts):
                 return False, tx_id, f"Receiver '{receiver}' doesn't match expected '{expected_name}'", data

        return True, tx_id, None, data

    except Exception as e:
        logging.error(f"ethiobank_receipts error: {e}")
        return False, None, str(e), None
