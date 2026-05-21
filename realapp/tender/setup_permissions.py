import frappe

def run():
    print("Starting setup of workflow roles and permissions...")
    create_roles_if_missing()
    setup_doctype_permissions()
    setup_workspace_permissions()
    setup_workflow()
    frappe.db.commit()
    print("Permissions setup successfully completed!")

def create_roles_if_missing():
    roles = [
        "Planning", "Planning Head", "Planning Manager", "Architect", 
        "Quantity Surveyor", "Procurement Team", "Contracts Team", 
        "Project Team", "Tender Committee", "Management", "Project Head"
    ]
    for role_name in roles:
        if not frappe.db.exists("Role", role_name):
            role = frappe.get_doc({
                "doctype": "Role",
                "role_name": role_name,
                "desk_access": 1
            })
            role.insert(ignore_permissions=True)
            print(f"Created role: {role_name}")
        else:
            print(f"Role already exists: {role_name}")

def setup_doctype_permissions():
    # Clear existing custom docperms for Tender Calendar
    frappe.db.delete("Custom DocPerm", {"parent": "Tender Calendar"})
    
    # Planning Team (Full Access)
    planning_roles = ["Planning", "Planning Head", "Planning Manager", "System Manager"]
    for role in planning_roles:
        frappe.get_doc({
            "doctype": "Custom DocPerm",
            "parent": "Tender Calendar",
            "parenttype": "DocType",
            "parentfield": "permissions",
            "role": role,
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "share": 1,
            "export": 1,
            "print": 1,
            "email": 1,
            "report": 1,
            "permlevel": 0
        }).insert(ignore_permissions=True)
        print(f"Set full permissions for {role}")
        
    # Other Workflow Roles (View + Edit, NO Create, NO Delete)
    other_roles = [
        "Architect", "Quantity Surveyor", "Procurement Team", 
        "Contracts Team", "Project Team", "Tender Committee", "Management", "Project Head"
    ]
    for role in other_roles:
        frappe.get_doc({
            "doctype": "Custom DocPerm",
            "parent": "Tender Calendar",
            "parenttype": "DocType",
            "parentfield": "permissions",
            "role": role,
            "read": 1,
            "write": 1,
            "create": 0,
            "delete": 0,
            "share": 1,
            "export": 1,
            "print": 1,
            "email": 1,
            "report": 1,
            "permlevel": 0
        }).insert(ignore_permissions=True)
        print(f"Set restricted edit permissions for {role}")

def setup_workspace_permissions():
    workspace = frappe.get_doc("Workspace", "Tender")
    # Clear the roles child table
    workspace.roles = []
    
    all_roles = [
        "Planning", "Planning Head", "Planning Manager", "Architect", 
        "Quantity Surveyor", "Procurement Team", "Contracts Team", 
        "Project Team", "Tender Committee", "Management", "Project Head", "System Manager"
    ]
    for role in all_roles:
        workspace.append("roles", {
            "role": role
        })
    workspace.save(ignore_permissions=True)
    print("Configured workspace permissions for Tender Workspace")

def setup_workflow():
    workflow_name = "Tender Calendar Workflow"
    
    # 1. Create Workflow States
    states_info = {
        "Tender Creation": "Primary",
        "Design Sample / Drawings": "Primary",
        "BOQ Submission": "Primary",
        "Vendor Finalisation": "Primary",
        "Technical Evaluation": "Primary",
        "Issue of Tender / Quotations": "Primary",
        "Pre-Bid Meeting": "Primary",
        "Quotation Collection / Rate Comparison": "Primary",
        "Supplier Negotiation - 1": "Primary",
        "Supplier Negotiation - 2": "Primary",
        "Order for Approval": "Warning",
        "Contract Agreement / Issue of Order": "Info",
        "Vendor Onboarding": "Info",
        "Completed": "Success"
    }
    for state, style in states_info.items():
        if not frappe.db.exists("Workflow State", state):
            ws = frappe.get_doc({
                "doctype": "Workflow State",
                "workflow_state_name": state,
                "style": style
            })
            ws.insert(ignore_permissions=True)
            print(f"Created Workflow State: {state}")

    # 2. Create Workflow Actions
    actions = [
        "Send for Design",
        "Submit Design",
        "Submit BOQ",
        "Start Technical Evaluation",
        "Complete Technical Evaluation",
        "Issue Tender",
        "Complete Pre-Bid Meeting",
        "Submit Quotations / Comparison",
        "Complete Negotiation 1",
        "Submit for Approval",
        "Approve Order",
        "Execute Contract",
        "Complete Onboarding",
        "Send Back"
    ]
    for action in actions:
        if not frappe.db.exists("Workflow Action Master", action):
            wa = frappe.get_doc({
                "doctype": "Workflow Action Master",
                "workflow_action_name": action
            })
            wa.insert(ignore_permissions=True)
            print(f"Created Workflow Action Master: {action}")

    # 3. Create/Update Workflow Document
    if frappe.db.exists("Workflow", workflow_name):
        frappe.delete_doc("Workflow", workflow_name)
        
    wf = frappe.get_doc({
        "doctype": "Workflow",
        "workflow_name": workflow_name,
        "document_type": "Tender Calendar",
        "workflow_state_field": "workflow_state",
        "is_active": 1,
        "states": [
            {"state": "Tender Creation", "doc_status": 0, "allow_edit": "Planning"},
            {"state": "Design Sample / Drawings", "doc_status": 0, "allow_edit": "Architect"},
            {"state": "BOQ Submission", "doc_status": 0, "allow_edit": "Quantity Surveyor"},
            {"state": "Vendor Finalisation", "doc_status": 0, "allow_edit": "Procurement Team"},
            {"state": "Technical Evaluation", "doc_status": 0, "allow_edit": "Project Team"},
            {"state": "Issue of Tender / Quotations", "doc_status": 0, "allow_edit": "Procurement Team"},
            {"state": "Pre-Bid Meeting", "doc_status": 0, "allow_edit": "Procurement Team"},
            {"state": "Quotation Collection / Rate Comparison", "doc_status": 0, "allow_edit": "Procurement Team"},
            {"state": "Supplier Negotiation - 1", "doc_status": 0, "allow_edit": "Procurement Team"},
            {"state": "Supplier Negotiation - 2", "doc_status": 0, "allow_edit": "Procurement Team"},
            {"state": "Order for Approval", "doc_status": 0, "allow_edit": "Tender Committee"},
            {"state": "Contract Agreement / Issue of Order", "doc_status": 0, "allow_edit": "Procurement Team"},
            {"state": "Vendor Onboarding", "doc_status": 0, "allow_edit": "Planning Head"},
            {"state": "Completed", "doc_status": 0, "allow_edit": "System Manager"}
        ],
        "transitions": [
            # Tender Creation -> Design Sample / Drawings
            {"state": "Tender Creation", "action": "Send for Design", "next_state": "Design Sample / Drawings", "allowed": "Planning"},
            {"state": "Tender Creation", "action": "Send for Design", "next_state": "Design Sample / Drawings", "allowed": "Planning Head"},
            {"state": "Tender Creation", "action": "Send for Design", "next_state": "Design Sample / Drawings", "allowed": "Planning Manager"},
            
            # Design Sample / Drawings -> BOQ Submission
            {"state": "Design Sample / Drawings", "action": "Submit Design", "next_state": "BOQ Submission", "allowed": "Architect"},
            
            # BOQ Submission -> Vendor Finalisation
            {"state": "BOQ Submission", "action": "Submit BOQ", "next_state": "Vendor Finalisation", "allowed": "Planning"},
            {"state": "BOQ Submission", "action": "Submit BOQ", "next_state": "Vendor Finalisation", "allowed": "Quantity Surveyor"},
            
            # Vendor Finalisation -> Technical Evaluation
            {"state": "Vendor Finalisation", "action": "Start Technical Evaluation", "next_state": "Technical Evaluation", "allowed": "Procurement Team"},
            
            # Technical Evaluation -> Issue of Tender / Quotations
            {"state": "Technical Evaluation", "action": "Complete Technical Evaluation", "next_state": "Issue of Tender / Quotations", "allowed": "Project Team"},
            {"state": "Technical Evaluation", "action": "Complete Technical Evaluation", "next_state": "Issue of Tender / Quotations", "allowed": "Procurement Team"},
            {"state": "Technical Evaluation", "action": "Complete Technical Evaluation", "next_state": "Issue of Tender / Quotations", "allowed": "Management"},
            
            # Issue of Tender / Quotations -> Pre-Bid Meeting
            {"state": "Issue of Tender / Quotations", "action": "Issue Tender", "next_state": "Pre-Bid Meeting", "allowed": "Procurement Team"},
            {"state": "Issue of Tender / Quotations", "action": "Issue Tender", "next_state": "Pre-Bid Meeting", "allowed": "Contracts Team"},
            
            # Pre-Bid Meeting -> Quotation Collection / Rate Comparison
            {"state": "Pre-Bid Meeting", "action": "Complete Pre-Bid Meeting", "next_state": "Quotation Collection / Rate Comparison", "allowed": "Procurement Team"},
            {"state": "Pre-Bid Meeting", "action": "Complete Pre-Bid Meeting", "next_state": "Quotation Collection / Rate Comparison", "allowed": "Contracts Team"},
            
            # Quotation Collection / Rate Comparison -> Supplier Negotiation - 1
            {"state": "Quotation Collection / Rate Comparison", "action": "Submit Quotations / Comparison", "next_state": "Supplier Negotiation - 1", "allowed": "Procurement Team"},
            {"state": "Quotation Collection / Rate Comparison", "action": "Submit Quotations / Comparison", "next_state": "Supplier Negotiation - 1", "allowed": "Contracts Team"},
            
            # Supplier Negotiation - 1 -> Supplier Negotiation - 2
            {"state": "Supplier Negotiation - 1", "action": "Complete Negotiation 1", "next_state": "Supplier Negotiation - 2", "allowed": "Procurement Team"},
            {"state": "Supplier Negotiation - 1", "action": "Complete Negotiation 1", "next_state": "Supplier Negotiation - 2", "allowed": "Contracts Team"},
            
            # Supplier Negotiation - 2 -> Order for Approval
            {"state": "Supplier Negotiation - 2", "action": "Submit for Approval", "next_state": "Order for Approval", "allowed": "Procurement Team"},
            {"state": "Supplier Negotiation - 2", "action": "Submit for Approval", "next_state": "Order for Approval", "allowed": "Contracts Team"},
            
            # Order for Approval -> Contract Agreement / Issue of Order
            {"state": "Order for Approval", "action": "Approve Order", "next_state": "Contract Agreement / Issue of Order", "allowed": "Tender Committee"},
            {"state": "Order for Approval", "action": "Approve Order", "next_state": "Contract Agreement / Issue of Order", "allowed": "Management"},
            
            # Contract Agreement / Issue of Order -> Vendor Onboarding
            {"state": "Contract Agreement / Issue of Order", "action": "Execute Contract", "next_state": "Vendor Onboarding", "allowed": "Procurement Team"},
            {"state": "Contract Agreement / Issue of Order", "action": "Execute Contract", "next_state": "Vendor Onboarding", "allowed": "Contracts Team"},
            
            # Vendor Onboarding -> Completed
            {"state": "Vendor Onboarding", "action": "Complete Onboarding", "next_state": "Completed", "allowed": "Planning Head"},
            {"state": "Vendor Onboarding", "action": "Complete Onboarding", "next_state": "Completed", "allowed": "Project Head"},

            # Send Back transitions
            {"state": "BOQ Submission", "action": "Send Back", "next_state": "Design Sample / Drawings", "allowed": "Planning"},
            {"state": "BOQ Submission", "action": "Send Back", "next_state": "Design Sample / Drawings", "allowed": "Quantity Surveyor"},
            {"state": "Technical Evaluation", "action": "Send Back", "next_state": "Vendor Finalisation", "allowed": "Project Team"},
            {"state": "Technical Evaluation", "action": "Send Back", "next_state": "Vendor Finalisation", "allowed": "Procurement Team"},
            {"state": "Technical Evaluation", "action": "Send Back", "next_state": "Vendor Finalisation", "allowed": "Management"},
            {"state": "Order for Approval", "action": "Send Back", "next_state": "Supplier Negotiation - 2", "allowed": "Tender Committee"},
            {"state": "Order for Approval", "action": "Send Back", "next_state": "Supplier Negotiation - 2", "allowed": "Management"},
            {"state": "Contract Agreement / Issue of Order", "action": "Send Back", "next_state": "Order for Approval", "allowed": "Procurement Team"},
            {"state": "Contract Agreement / Issue of Order", "action": "Send Back", "next_state": "Order for Approval", "allowed": "Contracts Team"}
        ]
    })
    wf.insert(ignore_permissions=True)
    print("Workflow Tender Calendar Workflow successfully created and activated!")
