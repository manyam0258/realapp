# Sales Booking Data Attachments implementation

I've completed the implementation of the attachments structure according to your specifications. Given the mix of single-document limits (`min: 1`) and multi-document requirements (`min: 2`), we utilized the Frappe best-practice pattern and achieved this via a consolidated list approach.

## Changes Made

### 1. New Attachments Tab
We injected a new Tab Break called **"Attachments"** into the `Sales Booking Data` DocType layout. This places all document uploads cleanly into their own section without cluttering the primary applicant/unit details.

### 2. Single Document Fields
For documents requiring exactly one attachment (or fewer than 1 like Legal Notices), explicit `Attach` fields have been created within the new Attachments Tab:
* Booking Form
* Agreement of Sales
* Letter of requests for extension of time for registration
* Tripartite Agreement
* Builder NOC
* Bank NOC
* Loan Processing
* Legal Notice 

### 3. Multiple Documents Child Table
For documents allowing multiple uploads (`min: 2`), we established the **SBD Attachment** Child DocType. 
This behaves as a unified table. When your internal users upload multiple Payment Receipts or Intimation Letters, they simply add a row to this new table in the Sales Booking Data, choose the Document Type from the dropdown, upload the file, and (optionally) leave any related remarks.

#### Supported multiple attachment categories:
* Customer payment receipts
* Milestone Intimation Letters
* Payment Intimation Letters (Demand Letters)
* TDS receipts
* Statement of accounts
* Customer Acknowledgements for referral paid cheques
* Customer email communications
* Internal note approvals
* Others

## Validation Results

* The `SBD Attachment` Child DocType was successfully generated natively in the metadata and set to standard tracking mode (`custom=0`).
* All fields and layout updates inside `Sales Booking Data` have been committed to the `sales_booking_data.json` source schema mapping.
* The system is fully ready for Frappe deployments and no explicit table-migrations/patches are required as the standard `.json` was refreshed.

> [!TIP]
> You can now visit any `Sales Booking Data` record in your system and you should immediately see the new "Attachments" tab with the fields rendering correctly.
