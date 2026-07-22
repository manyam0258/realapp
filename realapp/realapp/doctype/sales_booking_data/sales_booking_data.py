# Copyright (c) 2026, surendhranath and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import os

class SalesBookingData(Document):
	pass

@frappe.whitelist()
def consolidate_documents(docname):
    try:
        import fitz  # PyMuPDF
    except ImportError:
        frappe.throw("PyMuPDF (fitz) is not installed. Please contact administrator.")
        
    doc = frappe.get_doc("Sales Booking Data", docname)
    
    # Collect all file urls attached
    file_urls = []
    
    # 1. Single fields
    single_fields = [
        "booking_form", "agreement_of_sales", "extension_request_letter",
        "tripartite_agreement", "builder_noc", "bank_noc",
        "loan_processing", "legal_notice"
    ]
    for field in single_fields:
        val = doc.get(field)
        if val:
            file_urls.append(val)
            
    # 2. Multiple attachments table
    if doc.get("sbd_attachments"):
        for row in doc.get("sbd_attachments"):
            if row.attachment:
                file_urls.append(row.attachment)
                
    if not file_urls:
        frappe.throw("No documents attached to this record to consolidate.")
        
    merged_pdf = fitz.open()
    file_processed_count = 0
    
    site_path = frappe.get_site_path()
    
    for relative_url in file_urls:
        if relative_url.startswith("/files/"):
            # Public files
            file_path = os.path.join(site_path, "public", "files", relative_url.replace("/files/", ""))
        elif relative_url.startswith("/private/files/"):
            # Private files
            file_path = os.path.join(site_path, "private", "files", relative_url.replace("/private/files/", ""))
        else:
            # Maybe external URL
            continue
            
        if not os.path.exists(file_path):
            continue
            
        try:
            if file_path.lower().endswith('.pdf'):
                append_doc = fitz.open(file_path)
                merged_pdf.insert_pdf(append_doc)
                append_doc.close()
                file_processed_count += 1
            elif file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                img = fitz.open(file_path)
                pdfbytes = img.convert_to_pdf()
                img_doc = fitz.open("pdf", pdfbytes)
                merged_pdf.insert_pdf(img_doc)
                img_doc.close()
                img.close()
                file_processed_count += 1
        except Exception as e:
            frappe.log_error(title="PDF Consolidation Error", message=str(e))
            
    if file_processed_count == 0:
        frappe.throw("Could not process any of the attached files into a PDF.")
        
    merged_bytes = merged_pdf.write()
    merged_pdf.close()
    
    file_name = f"Consolidated_Docs_{doc.name}.pdf"
    
    # Save using frappe standard methods so it's tracked and accessible
    saved_file = frappe.get_doc({
        "doctype": "File",
        "file_name": file_name,
        "attached_to_doctype": "Sales Booking Data",
        "attached_to_name": doc.name,
        "attached_to_field": "",
        "folder": "Home/Attachments",
        "is_private": 0,
        "content": merged_bytes
    })
    saved_file.insert(ignore_permissions=True)
    
    return saved_file.file_url
    
