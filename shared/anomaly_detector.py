# Anomalies like:
# product not found
# Payment pending issues
# stock mismatch

from typing import List, Dict


def run_anomaly_checks(db) -> List[Dict]:
    anomalies = []

    # 1. Product not found
    q1 = """
    SELECT order_id
    FROM Orders
    WHERE product_id NOT IN (SELECT product_id FROM Products)
    """
    res = db.execute_query(q1)
    if res:
        anomalies.append({
            "type": "PRODUCT_NOT_FOUND",
            "count": len(res),
            "details": res
        })

    # 2. Payment pending > 30 days
    q2 = """
    SELECT invoice_id, customer_id, due_date
    FROM Invoices
    WHERE payment_status = 'PENDING'
      AND due_date < DATEADD(day, -30, GETDATE())
    """
    res = db.execute_query(q2)
    if res:
        anomalies.append({
            "type": "PAYMENT_DELAY",
            "count": len(res),
            "details": res
        })

    # 3. Stock mismatch
    q3 = """
    SELECT p.product_id, p.stock_qty, SUM(o.quantity) AS ordered_qty
    FROM Products p
    JOIN Orders o ON p.product_id = o.product_id
    GROUP BY p.product_id, p.stock_qty
    HAVING p.stock_qty < SUM(o.quantity)
    """
    res = db.execute_query(q3)
    if res:
        anomalies.append({
            "type": "STOCK_MISMATCH",
            "details": res
        })

    return anomalies
