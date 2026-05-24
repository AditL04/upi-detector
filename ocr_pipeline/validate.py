import re

UPI_PATTERN = re.compile(r"\b[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}\b")
TXN_PATTERN = re.compile(r"\b[a-zA-Z0-9]{10,30}\b")
AMOUNT_PATTERN = re.compile(r"(₹|rs\.?|inr)?\s?\d{1,3}(,\d{3})*(\.\d{1,2})?|\b\d+(\.\d{1,2})?\b", re.IGNORECASE)
DATE_PATTERN = re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{1,2}\s(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s\d{2,4}\b", re.IGNORECASE)
TIME_PATTERN = re.compile(r"\b\d{1,2}:\d{2}(\s?[APMapm]{2})?\b")

def normalize_text_list(text):
    return [str(t).strip() for t in text if str(t).strip()]

def valid_upi(text):
    text = normalize_text_list(text)
    return any(UPI_PATTERN.search(t) for t in text)

def txn_valid(text):
    text = normalize_text_list(text)
    return any(TXN_PATTERN.search(t) for t in text)

def amount_valid(text):
    text = normalize_text_list(text)
    return any(AMOUNT_PATTERN.search(t) for t in text)

def date_valid(text):
    text = normalize_text_list(text)
    return any(DATE_PATTERN.search(t) for t in text)

def time_valid(text):
    text = normalize_text_list(text)
    return any(TIME_PATTERN.search(t) for t in text)

def validation_score(text):
    score = 0
    score += int(valid_upi(text))
    score += int(txn_valid(text))
    score += int(amount_valid(text))
    score += int(date_valid(text))
    score += int(time_valid(text))
    return score

def validation_report(text):
    text = normalize_text_list(text)
    return {
        "upi_found": valid_upi(text),
        "txn_found": txn_valid(text),
        "amount_found": amount_valid(text),
        "date_found": date_valid(text),
        "time_found": time_valid(text),
        "score": validation_score(text)
    }