from fastapi import FastAPI, Query
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict

app = FastAPI(title="Vehicle Info API", version="1.0")


# -------------------------
# Data model for response
# -------------------------
class VehicleOut(BaseModel):
    ok: bool
    rc: str
    owner_name: Optional[str] = None
    father_name: Optional[str] = None
    owner_serial_no: Optional[str] = None
    model_name: Optional[str] = None
    maker_model: Optional[str] = None
    vehicle_class: Optional[str] = None
    fuel_type: Optional[str] = None
    fuel_norms: Optional[str] = None
    reg_date: Optional[str] = None
    insurance_company: Optional[str] = None
    insurance_no: Optional[str] = None
    insurance_expiry: Optional[str] = None
    insurance_upto: Optional[str] = None
    fitness_upto: Optional[str] = None
    tax_upto: Optional[str] = None
    puc_no: Optional[str] = None
    puc_upto: Optional[str] = None
    financier_name: Optional[str] = None
    rto: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    note: Optional[str] = None
    error: Optional[str] = None


# -------------------------
# Scraper function
# -------------------------
def get_vehicle_details(rc_number: str) -> Dict:
    """Fetches comprehensive vehicle details from vahanx.in."""
    rc = rc_number.strip().upper()
    url = f"https://vahanx.in/rc-search/{rc}"

    headers = {
        "Host": "vahanx.in",
        "Connection": "keep-alive",
        "sec-ch-ua": "\"Chromium\";v=\"130\", \"Google Chrome\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": "\"Android\"",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Referer": "https://vahanx.in/rc-search",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
    except requests.exceptions.RequestException as e:
        return {"ok": False, "rc": rc, "error": f"Network error: {e}"}
    except Exception as e:
        return {"ok": False, "rc": rc, "error": str(e)}

    def get_value(label):
        """Extracts <p> text next to a <span> containing `label`"""
        try:
            div = soup.find("span", string=lambda t: t and label in t).find_parent("div")
            return div.find("p").get_text(strip=True)
        except AttributeError:
            return None

    data = {
        "ok": True,
        "rc": rc,
        "owner_name": get_value("Owner Name"),
        "father_name": get_value("Father's Name"),
        "owner_serial_no": get_value("Owner Serial No"),
        "model_name": get_value("Model Name"),
        "maker_model": get_value("Maker Model"),
        "vehicle_class": get_value("Vehicle Class"),
        "fuel_type": get_value("Fuel Type"),
        "fuel_norms": get_value("Fuel Norms"),
        "reg_date": get_value("Registration Date"),
        "insurance_company": get_value("Insurance Company"),
        "insurance_no": get_value("Insurance No"),
        "insurance_expiry": get_value("Insurance Expiry"),
        "insurance_upto": get_value("Insurance Upto"),
        "fitness_upto": get_value("Fitness Upto"),
        "tax_upto": get_value("Tax Upto"),
        "puc_no": get_value("PUC No"),
        "puc_upto": get_value("PUC Upto"),
        "financier_name": get_value("Financier Name"),
        "rto": get_value("Registered RTO"),
        "address": get_value("Address"),
        "city": get_value("City Name"),
        "phone": get_value("Phone"),
        "note": "✅ Android scraper working!"
    }

    # If nothing found → mark as failure
    if not any(v for k, v in data.items() if k not in ["ok", "rc", "note"]):
        data["ok"] = False
        data["error"] = "No records found for this RC number"

    return data


# -------------------------
# API endpoint
# -------------------------
@app.get("/vehicle", response_model=VehicleOut)
def get_vehicle(rc: str = Query(..., min_length=6, max_length=12)):
    return get_vehicle_details(rc)
