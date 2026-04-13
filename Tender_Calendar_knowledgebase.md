
# **Tender Calendar Management System (Frappe / ERPNext)**

## **🎯 Objective**

Build a unified Tender Calendar system that:

1. Captures complete tender planning data (from master sheet)  
2. Drives procurement lifecycle (BOQ → Quotation → Order)  
3. Enables cascading impact across stages  
4. Bridges Project & Procurement teams  
5. Generates all required reports from a single source  
6. Provides proactive alerts & decision support

---

# **🧱 CORE PRINCIPLE**

👉 Single Source of Truth  
👉 One Primary DocType → "Tender Calendar"  
👉 All reports are derived views

---

# **📊 SOURCE UNDERSTANDING**

## **Master Sheet (Primary Data Model)**

From Tender Calendar:

* Work Package  
* Project Type  
* BOQ Dates  
* Tender Stages  
* Target Dates  
* Vendor Planning  
* Contract Value  
* Execution tracking

## **Derived Reports:**

### **1\. BOQ Tracker**

Tracks:

* Planned vs Submitted  
* Yet to submit

### **2\. Quotation Tracker**

Tracks:

* Vendor readiness  
* RFQ progress

### **3\. Order Tracker**

Tracks:

* Order issued vs pending

### **4\. Combined Tracker**

Tracks:

* Month-wise pipeline of BOQ \+ Orders

---

# **🧱 PRIMARY DOCTYPE: Tender Calendar**

## **🔹 Section 1: Identification**

* Sl\_no  
* project (Link)  
* work\_package  
* category  
* sub\_category

## **🔹 Section 2: Project Context**

* project\_type (Project / Tower Wise / Club House)  
* status (Finalised / Not Finalised)

## **🔹 Section 3: Procurement Readiness**

* design\_sample\_approval  
* indigenous\_import  
* min\_vendors\_required

## **🔹 Section 4: BOQ Tracking**

* boq\_submission\_date (Planned)  
* boq\_submitted\_date (Actual)  
* boq\_status (Yet to Submit / Submitted / NA)

## **🔹 Section 5: Tender Lifecycle**

* pre\_bid\_date  
* tender\_issue\_date  
* approval\_date  
* contract\_date  
* mobilization\_date

## **🔹 Section 6: Execution**

* target\_date  
* actual\_work\_start  
* no\_of\_days

## **🔹 Section 7: Construction Link**

* structure\_schedule

## **🔹 Section 8: Vendor Tracking**

* vendors\_to\_onboard  
* vendor\_count

## **🔹 Section 9: Financial**

* contract\_value\_lakhs

## **🔹 Section 10: Status & Remarks**

* order\_status  
* remarks  
* delay\_info

---

# **⚙️ CASCADING ENGINE (CONFIGURABLE)**

## **🔹 Global Settings: Tender Settings**

* enable\_cascading  
* default\_mode:  
  * Manual  
  * Suggestion  
  * Auto  
* allow\_override  
* require\_approval\_for\_cascade  
* max\_cascade\_days

---

## **🔹 Document Level**

* enable\_cascading  
* cascading\_mode  
* lock\_dates  
* is\_critical\_tender

---

## **🔹 Stage Level (Optional)**

* is\_fixed\_milestone  
* allow\_stage\_shift

---

# **🔁 CASCADING LOGIC**

When delay occurs:

IF mode \= Manual:  
→ Do nothing

IF mode \= Suggestion:  
→ Show impact preview

IF mode \= Auto:  
→ Shift all dependent dates

---

## **Example Flow**

BOQ delayed by 5 days:

System computes:

* Tender Issue → \+5 days  
* Approval → \+7 days  
* Contract → \+10 days  
* Mobilization → \+15 days

---

# **🧠 IMPACT ENGINE**

## **Fields**

* delay\_days  
* impact\_level (Low / Medium / High / Critical)  
* impacted\_stages  
* current\_stage

---

## **Logic**

Early stage delay → Higher impact

---

# **🔔 NOTIFICATION ENGINE**

## **Roles**

* project\_owner  
* procurement\_owner

---

## **Triggers**

### **1\. Reminder**

* 3 days before deadline

### **2\. Delay Alert**

* If missed date

### **3\. Cascade Alert**

* If impact detected

---

## **Notification Example**

"BOQ delayed → Contract & Mobilization impacted"

---

# **📊 REPORTS (DERIVED FROM SAME DOCTYPE)**

---

## **1\. BOQ Status Report**

(Source: )

Columns:

* Target Month  
* Work Package  
* BOQ Status  
* Order Status

---

## **2\. Quotation Status Report**

(Source: )

Tracks:

* Vendor readiness  
* RFQ progress

---

## **3\. Order Status Report**

(Source: )

Tracks:

* Orders issued  
* Pending approvals

---

## **4\. Combined Tracker**

(Source: )

Tracks:

* Month-wise pipeline  
* BOQ \+ Order flow

---

## **5\. Master Tender Calendar**

(Source: )

Full operational view

---

# **📅 CALENDAR VIEW**

Each record generates:

* Pre-Bid Event  
* Tender Issue Event  
* Approval Event  
* Contract Event  
* Mobilization Event

---

# **📊 DASHBOARDS**

## **Project Dashboard**

* Delays  
* Mobilization risk  
* Critical tenders

## **Procurement Dashboard**

* BOQ pending  
* RFQ pending  
* Orders pending

---

# **🔗 ERPNext INTEGRATION**

* RFQ creation  
* Supplier Quotation tracking  
* Purchase Order creation

---

# **⚠️ RISKS & CONTROLS**

## **Risk: Auto changes reduce trust**

→ Add audit trail

## **Risk: Over cascading**

→ Add max limit

## **Risk: Fixed dates**

→ Mark milestones as fixed

## **Risk: Team conflict**

→ Add approval workflow

---

# **🧩 FINAL ARCHITECTURE**

Tender Calendar  
↓  
Cascading Engine  
↓  
Impact Engine  
↓  
Notification Engine  
↓  
Reports & Dashboards

---

# **🚀 OUTCOME**

This system becomes:

👉 Procurement Planning Engine  
👉 Project Execution Controller  
👉 Cross-Team Alignment Tool

---

# **🔥 IMPLEMENTATION STRATEGY**

Phase 1:

* DocType \+ Reports

Phase 2:

* Notifications

Phase 3:

* Cascading (Suggestion Mode)

Phase 4:

* Auto Mode \+ Approvals

---

# **💡 KEY DESIGN RULE**

"Excel Structure is the System — Logic makes it Intelligent"

