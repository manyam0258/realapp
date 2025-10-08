# Copyright (c) 2025, surendhranath
# For license information, please see license.txt

import frappe
from frappe.utils import today, getdate


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)

    # 🔹 Add summary metrics
    summary = get_summary(data)

    return columns, data, None, None, summary


def get_columns():
    return [
        {"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 120},
        {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 100},
        {"label": "Unit", "fieldname": "unit", "fieldtype": "Link", "options": "Unit", "width": 120},
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": "Milestone", "fieldname": "milestone", "fieldtype": "Data", "width": 150},
        {"label": "Invoice No", "fieldname": "invoice_no", "fieldtype": "Link", "options": "Sales Invoice", "width": 150},
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": "Due Date", "fieldname": "due_date", "fieldtype": "Date", "width": 100},
        {"label": "Invoice Amount", "fieldname": "invoice_amount", "fieldtype": "Currency", "width": 120},
        {"label": "Paid Amount", "fieldname": "paid_amount", "fieldtype": "Currency", "width": 120},
        {"label": "Outstanding", "fieldname": "outstanding", "fieldtype": "Currency", "width": 120},
        {"label": "Last Payment Date", "fieldname": "last_payment_date", "fieldtype": "Date", "width": 120},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": "Last Remark", "fieldname": "last_remark", "fieldtype": "Small Text", "width": 200},
    ]


def get_data(filters):
    conditions = ["si.docstatus = 1"]
    values = {}

    if filters.get("project"):
        conditions.append("bo.project = %(project)s")
        values["project"] = filters["project"]

    if filters.get("block"):
        conditions.append("bo.block = %(block)s")
        values["block"] = filters["block"]

    if filters.get("unit"):
        conditions.append("bo.unit = %(unit)s")
        values["unit"] = filters["unit"]

    if filters.get("customer"):
        conditions.append("si.customer = %(customer)s")
        values["customer"] = filters["customer"]

    if filters.get("milestone"):
        conditions.append("sii.description = %(milestone)s")
        values["milestone"] = filters["milestone"]

    if filters.get("from_date") and filters.get("to_date"):
        conditions.append("si.due_date BETWEEN %(from_date)s AND %(to_date)s")
        values["from_date"] = filters["from_date"]
        values["to_date"] = filters["to_date"]

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT
            bo.project,
            bo.block,
            bo.unit,
            si.customer,
            sii.description AS milestone,
            si.name AS invoice_no,
            si.posting_date,
            si.due_date,
            si.rounded_total AS invoice_amount,
            IFNULL(SUM(per.allocated_amount), 0) AS paid_amount,
            (si.rounded_total - IFNULL(SUM(per.allocated_amount), 0)) AS outstanding,
            MAX(pe.posting_date) AS last_payment_date
        FROM
            `tabSales Invoice` si
        JOIN
            `tabSales Invoice Item` sii ON sii.parent = si.name
        LEFT JOIN
            `tabBooking Order` bo ON bo.name = si.booking_order
        LEFT JOIN
            `tabPayment Entry Reference` per ON per.reference_name = si.name AND per.docstatus = 1
        LEFT JOIN
            `tabPayment Entry` pe ON pe.name = per.parent
        WHERE {where_clause}
        GROUP BY si.name, sii.name
        ORDER BY si.due_date, bo.project, bo.block, bo.unit
    """

    data = frappe.db.sql(query, values, as_dict=True)

    # 🔹 Enrich rows with Status + Last Remark
    for row in data:
        row["status"] = get_status(row)
        row["last_remark"] = get_last_remark(row["invoice_no"])

    return data


def get_status(row):
    today_date = getdate(today())   # ensure it's a datetime.date

    due_date = row.get("due_date")
    if due_date and isinstance(due_date, str):
        due_date = getdate(due_date)

    if row["outstanding"] <= 0:
        return "Fully Paid"
    elif row["paid_amount"] == 0:
        return "Pending"
    elif due_date and due_date < today_date:
        return "Overdue"
    else:
        return "Partially Paid"


def get_last_remark(invoice_no):
    """Fetch last comment/note on Sales Invoice"""
    remark = frappe.db.sql("""
        SELECT content
        FROM `tabComment`
        WHERE reference_doctype = 'Sales Invoice'
          AND reference_name = %s
        ORDER BY creation DESC
        LIMIT 1
    """, (invoice_no,))
    return remark[0][0] if remark else ""


def get_summary(data):
    """Generate summary KPIs for top of report"""
    total_invoices = len(data)
    total_amount = sum(d.get("invoice_amount", 0) for d in data)
    total_paid = sum(d.get("paid_amount", 0) for d in data)
    total_outstanding = sum(d.get("outstanding", 0) for d in data)
    overdue_amount = sum(d.get("outstanding", 0) for d in data if d.get("status") == "Overdue")

    return [
        {"label": "Total Invoices", "value": total_invoices, "indicator": "Blue"},
        {"label": "Total Invoice Amount", "value": total_amount, "datatype": "Currency", "indicator": "Blue"},
        {"label": "Total Collected", "value": total_paid, "datatype": "Currency", "indicator": "Green"},
        {"label": "Total Outstanding", "value": total_outstanding, "datatype": "Currency", "indicator": "Red"},
        {"label": "Overdue Amount", "value": overdue_amount, "datatype": "Currency", "indicator": "Orange"},
    ]
