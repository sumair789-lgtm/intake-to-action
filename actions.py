"""
Notification logic ab doc_type-aware hai.
Amount-threshold sirf invoices ke liye maani rakhta hai.
"""

AMOUNT_THRESHOLD = 1000.0


def check_and_notify(doc_type: str, extracted_obj, record_id: int):
    alerts = []
    data = extracted_obj.model_dump()

    if doc_type == "invoice" and data.get("total_amount", 0) > AMOUNT_THRESHOLD:
        alerts.append(
            f"HIGH AMOUNT ALERT: Record #{record_id} ({data.get('vendor_name')}) -- "
            f"{data.get('total_amount')} {data.get('currency')} -- threshold se zyada."
        )

    if not data.get("confidence_flag", True):
        alerts.append(f"LOW CONFIDENCE: Record #{record_id} ({doc_type}) -- manual review chahiye.")

    for alert in alerts:
        print(f"[NOTIFICATION] {alert}")

    return alerts
