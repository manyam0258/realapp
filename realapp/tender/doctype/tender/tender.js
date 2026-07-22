// Copyright (c) 2026, surendhranath and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tender", {
    refresh(frm) {
        // ─── 1. ALL CONTROLLED FIELDS (CONSOLIDATED FROM CLIENT SCRIPT) ───
        const tab1_fields = [
            "sno", "work", "custom_work_package", "data_reference", "initiated_date", 
            "block_name", "category", "custom_work_category", "ref_no", "project", 
            "from", "to", "unit", "custom_all_units", "new__amd", 
            "required_shortlisted_vendors", "no_of_vendors_to_be_onboarded_for_the_project", 
            "order_type", "indigenous_import", "approx_value_in_lakhs", "others", 
            "no_of_days_planned", "target_date", "boq_submission_days_planned", 
            "boq_submission_target_date", "custom_boq_submission_target", "vendor_evaluation", 
            "introduction_meet_days_planned", "vendor_evaluation_target_date", 
            "floating_enquiries_days_planned", "floating_enquiries_target_date", 
            "pre_bid_no_of_days_planned", "pre_bid_target_date", "quotation_1_days_planned",
            "quotation_1_target_date", "quotation_2_days_planned", "quotation_2_target_date",
            "order_approval_days_planned", "order_approval_target_date", "agreement_no_of_days_planned",
            "agreement_target_date", "introduction_meeting", "introduction_meeting_days_planned",
            "introduction_meet_days_plan", "vendor_days_planned", "vendor_mobilization_target_date"
        ];

        const tab2_fields = [
            "design_sample_days_planned", "revised_planned_date", "work_initiation", 
            "submission_date", "design_sample_target_date", "duration_left", 
            "revision_status", "submission_status", "schematic_attachments", "remarks", "send_back_remarks"
        ];

        const tab3_fields = [
            "boq_no_of_days_planned", "revised_date", "boq_work_initiation", 
            "boq_submission_date", "boq_target_date", "boq_duration_left", 
            "boq_revision_status", "boq_submission_status", "boq_attachments",
            "boq_remarks", "boq_send_back_remarks"
        ];

        const tab4_fields = [
            "vendor_evaluation_days_planned", "vendor_evaluation_revised_planned_date", 
            "vendor_evaluation_work_initiation", "vendor_evaluation_submission_date", 
            "vendor_target_date", "vendor_evaluation_duration_left", 
            "vendor_evaluation_revision_status", "vendor_evaluation_submission_status", "vendor_evaluation_attachments", 
            "floating_enquiries_no_of_days_planned", "floating_enquiries_revised_planned_date", 
            "floating_enquiries_work_initiation", "floating_enquiries_submission_date", 
            "floating_enquiries_target", "floating_enquiries_duration_left", 
            "floating_enquiries_revision_status", "floating_enquiries_submission_status", "floating_enquiries_attachments", 
            "pre_bid_technical_meeting_no_of_days_planned", "pre_bid_technical_meeting_revised_planned_date", 
            "pre_bid_technical_meeting_work_initiation", "pre_bid_technical_meeting_submission_date", 
            "pre_bid_technical_meeting_target_date", "pre_bid_technical_meeting_duration_left", 
            "pre_bid_technical_meeting_revision_status", "pre_bid_technical_meeting_submission_status", "pre_bid_technical_meeting_attachments", 
            "negotiations_1_days_plan", "negotiations_1_rev_plan_date", 
            "negotiations_1_work_initiation", "negotiations_1_submit_date", 
            "negotiations_1_target_date", "negotiations_1_duration_left", 
            "negotiations_1_revision_status", "negotiations_1_submit_status", 
            "negotiation_1_attachments", "negotiations_2_days_plan", 
            "negotiations_2_rev_plan_date", "negotiations_2_work_initiation", 
            "negotiations_2_submit_date", "negotiations_2_target_date", 
            "negotiations_2_duration_left", "negotiations_2_revision_status", 
            "negotiations_2_submit_status", "negotiation_2_attachments",
            "evaluation_remarks", "evaluation_send_back_remarks"
        ];

        const tab5_fields = [
            "order_approval_days", "order_approval_revised_date", "order_approval_work_initiation", 
            "order_approval_submit_date", "order_approval_target", "order_approval_duration_left", 
            "order_approval_revision_status", "order_approval_submit_status", 
            "order_approval_attachments", "agreement_order_days_planned", "agreement_order_revised_plan_date", 
            "agreement_order_work_initiation", "agreement_order_submit_date", 
            "agreement_order_target_date", "agreement_order_duration_left", 
            "agreement_order_revision_status", "agreement_order_submission", 
            "agreement_order_attachments", "finalized_vendor_name", "contact_details", "order_closure_remarks", "order_closure_send_back_remarks"
        ];

        const tab6_fields = [
            "final_vendor_name", "vendor_contact_details", "introduction_days_planned", 
            "introduction_revised_planned_date", "introduction_work_initiation", 
            "introduction_submission_date", "introduction_target_date", "introduction_duration_left", 
            "introduction_revision_status", "introduction_submission_status", "introduction_meeting_attachments", "mobilization_days_planned", 
            "mobilization_revised_planned_date", "mobilization_work_initiation", "mobilization_submit_date", 
            "mobilization_target_date", "mobilization_duration_left", "mobilization_revision_status", 
            "mobilization_submit_status", "mobilization_attachments", "vendor_onboarding_remarks", "vendor_onboarding_send_back_remarks"
        ];

        // ─── 2. UTILITY HELPERS FOR VISIBILITY ───
        function set_fields_state(fields, hidden, read_only) {
            fields.forEach(field => {
                if (frm.fields_dict[field]) {
                    frm.set_df_property(field, "hidden", hidden);
                    frm.set_df_property(field, "read_only", read_only);
                    frm.refresh_field(field); // Critical: ensures value re-binds after toggling
                }
            });
        }

        function set_tab_visible(tab_fieldname, visible) {
            frm.set_df_property(tab_fieldname, "hidden", visible ? 0 : 1);
            
            let tab_link = frm.get_field(tab_fieldname)?.$link;
            let tab_wrapper = frm.get_field(tab_fieldname)?.$wrapper;

            if (tab_link && tab_link.length) {
                tab_link.closest("li").toggle(visible);
            } else {
                $(`a[data-fieldname="${tab_fieldname}"].nav-link`).closest("li").toggle(visible);
            }
            if (tab_wrapper && tab_wrapper.length) {
                tab_wrapper.toggle(visible);
            }
        }

        function set_tab_remarks_only(fields, remarks_field) {
            fields.forEach(field => {
                if (frm.fields_dict[field]) {
                    if (field === remarks_field) {
                        frm.set_df_property(field, "hidden", 0);
                        frm.set_df_property(field, "read_only", 1);
                    } else {
                        frm.set_df_property(field, "hidden", 1);
                    }
                    frm.refresh_field(field);
                }
            });
        }

        // ─── 3. PRECISE ROLE-BASED VISIBILITY ───
        let show_tab1 = false;
        let show_tab2 = false;
        let show_tab3 = false;
        let show_tab4 = false;
        let show_tab5 = false;
        let show_tab6 = false;

        let edit_tab1 = false;
        let edit_tab2 = false;
        let edit_tab3 = false;
        let edit_tab4 = false;
        let edit_tab5 = false;
        let edit_tab6 = false;

        let show_tab2_remarks_only = false;
        let show_tab3_remarks_only = false;
        let show_tab4_remarks_only = false;
        let show_tab5_remarks_only = false;
        let show_tab6_remarks_only = false;

        const roles = frappe.user_roles || [];

        if (roles.includes("System Manager")) {
            show_tab1 = true;
            show_tab2 = true;
            show_tab3 = true;
            show_tab4 = true;
            show_tab5 = true;
            show_tab6 = true;
            edit_tab1 = true;
            edit_tab2 = true;
            edit_tab3 = true;
            edit_tab4 = true;
            edit_tab5 = true;
            edit_tab6 = true;
        } else {
            // Tab 1 (Initiation) is visible to all roles (but editable only by Planning)
            show_tab1 = true;

            if (roles.includes("Planning")) {
                edit_tab1 = true;
                show_tab6 = true;
                edit_tab6 = true;
                show_tab4 = true; // Previous stage read-only
                show_tab5 = true; // Previous stage read-only
                if (frm.doc.workflow_state === "Tender Creation" && frm.doc.send_back_remarks) {
                    show_tab2 = true;
                    show_tab2_remarks_only = true;
                }
            }
            if (roles.includes("Architect")) {
                show_tab2 = true;
                edit_tab2 = true;
                if (frm.doc.workflow_state === "Design Sample / Drawings" && frm.doc.boq_send_back_remarks) {
                    show_tab3 = true;
                    show_tab3_remarks_only = true;
                }
            }
            if (roles.includes("Quantity Surveyor")) {
                show_tab2 = true; // Previous stage read-only
                show_tab3 = true;
                edit_tab3 = true;
                if (frm.doc.workflow_state === "BOQ Submission" && frm.doc.evaluation_send_back_remarks) {
                    show_tab4 = true;
                    show_tab4_remarks_only = true;
                }
            }
            if (roles.includes("Procurement Team")) {
                show_tab3 = true; // Previous stage read-only

                if (frm.doc.workflow_state === "Evaluation Process") {
                    show_tab4 = true;
                    edit_tab4 = true;
                    if (frm.doc.order_closure_send_back_remarks) {
                        show_tab5 = true;
                        show_tab5_remarks_only = true;
                    }
                } else if (frm.doc.workflow_state === "Order Closure") {
                    show_tab4 = true; // Previous stage read-only
                    show_tab5 = true;
                    edit_tab5 = true;
                    if (frm.doc.vendor_onboarding_send_back_remarks) {
                        show_tab6 = true;
                        show_tab6_remarks_only = true;
                    }
                } else {
                    // For all other states (e.g. Vendor Finalisation, Completed)
                    show_tab4 = true;
                    show_tab5 = true;
                }
            }
        }

        // Apply tab visibility
        set_tab_visible("initiation_tab", show_tab1);
        set_tab_visible("schematic_readiness_tab", show_tab2);
        set_tab_visible("tab_3_tab", show_tab3);
        set_tab_visible("tab_4_tab", show_tab4);
        set_tab_visible("order_closure_tab", show_tab5);
        set_tab_visible("tab_5_tab", show_tab6);

        // Apply field states (hidden, read_only)
        set_fields_state(tab1_fields, !show_tab1, !edit_tab1);
        set_fields_state(tab2_fields, !show_tab2, !edit_tab2);
        set_fields_state(tab3_fields, !show_tab3, !edit_tab3);
        set_fields_state(tab4_fields, !show_tab4, !edit_tab4);
        set_fields_state(tab5_fields, !show_tab5, !edit_tab5);
        set_fields_state(tab6_fields, !show_tab6, !edit_tab6);

        // Overrides for Tab Remarks Only view
        if (show_tab2_remarks_only) {
            set_tab_remarks_only(tab2_fields, "send_back_remarks");
        }
        if (show_tab3_remarks_only) {
            set_tab_remarks_only(tab3_fields, "boq_send_back_remarks");
        }
        if (show_tab4_remarks_only) {
            set_tab_remarks_only(tab4_fields, "evaluation_send_back_remarks");
        }
        if (show_tab5_remarks_only) {
            set_tab_remarks_only(tab5_fields, "order_closure_send_back_remarks");
        }
        if (show_tab6_remarks_only) {
            set_tab_remarks_only(tab6_fields, "vendor_onboarding_send_back_remarks");
        }

        // ─── 4. SILENT UPDATE OF CALCULATED FIELDS ───
        // Run section updates silently to prevent setting the form dirty on load / refresh
        update_design_sample_section(frm, true);
        update_boq_section(frm, true);
        update_vendor_evaluation_section(frm, true);
        update_introduction_section(frm, true);
        update_order_closure_section(frm, true);
        update_vendor_onboarding_section(frm, true);
        update_approx_value_in_words(frm);
    },
    approx_value_in_lakhs(frm) {
        update_approx_value_in_words(frm);
    },
    order_type(frm) {
        if (frm.doc.order_type === "Service") {
            frm.set_value("indigenous_import", "NA");
        }
    },
    initiated_date(frm) {
        calculate_all_dates(frm);
        update_design_sample_section(frm);
    },
    introduction_submission_date(frm) {
        if (frm.doc.introduction_submission_date) {
            frm.set_value("mobilization_work_initiation", get_next_working_day(frm.doc.introduction_submission_date));
        }
        update_introduction_section(frm);
        update_vendor_onboarding_section(frm);
    },
    mobilization_submit_date(frm) {
        update_vendor_onboarding_section(frm);
    },
    no_of_days_planned(frm) {
        calculate_all_dates(frm);
        update_design_sample_section(frm);
    },
    work_initiation(frm) {
        update_design_sample_section(frm);
    },
    submission_date(frm) {
        if (frm.doc.submission_date) {
            frm.set_value("boq_work_initiation", get_next_working_day(frm.doc.submission_date));
        }
        update_design_sample_section(frm);
        update_boq_section(frm);
        update_vendor_evaluation_section(frm);
    },
    finalized_vendor_name(frm) {
        update_vendor_onboarding_section(frm);
    },
    contact_details(frm) {
        update_vendor_onboarding_section(frm);
    },
    boq_submission_date(frm) {
        if (frm.doc.boq_submission_date) {
            frm.set_value("vendor_evaluation_work_initiation", get_next_working_day(frm.doc.boq_submission_date));
        }
        update_boq_section(frm);
        update_vendor_evaluation_section(frm);
    },
    boq_submission_days_planned(frm) {
        calculate_all_dates(frm);
        update_boq_section(frm);
    },
    boq_work_initiation(frm) {
        update_boq_section(frm);
    },
    vendor_evaluation_work_initiation(frm) {
        update_vendor_evaluation_section(frm);
    },
    floating_enquiries_work_initiation(frm) {
        update_order_closure_section(frm);
    },
    pre_bid_technical_meeting_work_initiation(frm) {
        update_order_closure_section(frm);
    },
    negotiations_1_work_initiation(frm) {
        update_order_closure_section(frm);
    },
    negotiations_2_work_initiation(frm) {
        update_order_closure_section(frm);
    },
    order_approval_work_initiation(frm) {
        update_order_closure_section(frm);
    },
    agreement_order_work_initiation(frm) {
        update_order_closure_section(frm);
    },
    introduction_work_initiation(frm) {
        update_introduction_section(frm);
    },
    mobilization_work_initiation(frm) {
        update_vendor_onboarding_section(frm);
    },
    mobilization_days_planned(frm) {
        calculate_all_dates(frm);
        update_vendor_onboarding_section(frm);
    },
    vendor_days_planned(frm) {
        calculate_all_dates(frm);
    },
    vendor_evaluation_submission_date(frm) {
        if (frm.doc.vendor_evaluation_submission_date) {
            frm.set_value("floating_enquiries_work_initiation", get_next_working_day(frm.doc.vendor_evaluation_submission_date));
        }
        update_vendor_evaluation_section(frm);
        update_order_closure_section(frm);
    },
    floating_enquiries_submission_date(frm) {
        if (frm.doc.floating_enquiries_submission_date) {
            frm.set_value("pre_bid_technical_meeting_work_initiation", get_next_working_day(frm.doc.floating_enquiries_submission_date));
        }
        update_order_closure_section(frm);
    },
    pre_bid_technical_meeting_submission_date(frm) {
        if (frm.doc.pre_bid_technical_meeting_submission_date) {
            frm.set_value("negotiations_1_work_initiation", get_next_working_day(frm.doc.pre_bid_technical_meeting_submission_date));
        }
        update_order_closure_section(frm);
    },
    negotiations_1_submit_date(frm) {
        if (frm.doc.negotiations_1_submit_date) {
            frm.set_value("negotiations_2_work_initiation", get_next_working_day(frm.doc.negotiations_1_submit_date));
        }
        update_order_closure_section(frm);
    },
    negotiations_2_submit_date(frm) {
        if (frm.doc.negotiations_2_submit_date) {
            frm.set_value("order_approval_work_initiation", get_next_working_day(frm.doc.negotiations_2_submit_date));
        }
        update_order_closure_section(frm);
    },
    order_approval_submit_date(frm) {
        if (frm.doc.order_approval_submit_date) {
            frm.set_value("agreement_order_work_initiation", get_next_working_day(frm.doc.order_approval_submit_date));
        }
        update_order_closure_section(frm);
    },
    agreement_order_submit_date(frm) {
        if (frm.doc.agreement_order_submit_date) {
            frm.set_value("introduction_work_initiation", get_next_working_day(frm.doc.agreement_order_submit_date));
        }
        update_introduction_section(frm);
        update_order_closure_section(frm);
    },
    introduction_meet_days_planned(frm) {
        calculate_all_dates(frm);
    },
    floating_enquiries_days_planned(frm) {
        calculate_all_dates(frm);
    },
    pre_bid_no_of_days_planned(frm) {
        calculate_all_dates(frm);
    },
    quotation_1_days_planned(frm) {
        calculate_all_dates(frm);
    },
    quotation_2_days_planned(frm) {
        calculate_all_dates(frm);
    },
    order_approval_days_planned(frm) {
        calculate_all_dates(frm);
    },
    agreement_no_of_days_planned(frm) {
        calculate_all_dates(frm);
    },
    introduction_meeting_days_planned(frm) {
        calculate_all_dates(frm);
    },
    data_reference(frm) {
        if (frm.doc.data_reference === "Order Request Mail") {
            frm.set_value("ref_no", "");
        }
    },
    before_workflow_action(frm) {
        let action = frm.selected_workflow_action;
        let today = frappe.datetime.get_today();
        if (action === "Submit Design") {
            frm.set_value("submission_date", today);
        } else if (action === "Submit BOQ") {
            frm.set_value("boq_submission_date", today);
        } else if (action === "Submit Evaluation") {
            frm.set_value("vendor_evaluation_submission_date", today);
            frm.set_value("floating_enquiries_submission_date", today);
            frm.set_value("pre_bid_technical_meeting_submission_date", today);
            frm.set_value("negotiations_1_submit_date", today);
            frm.set_value("negotiations_2_submit_date", today);
        } else if (action === "Submit Order Closure") {
            frm.set_value("order_approval_submit_date", today);
            frm.set_value("agreement_order_submit_date", today);
        } else if (action === "Submit for Vendor Onboarding" || action === "Vendor Onboarded") {
            frm.set_value("introduction_submission_date", today);
            frm.set_value("mobilization_submit_date", today);
        } else if (action === "Send Back") {
            let current_state = frm.doc.workflow_state;
            let fieldname = null;
            let field_label = "";

            if (current_state === "Design Sample / Drawings") {
                fieldname = "send_back_remarks";
                field_label = "Send Back Remarks";
            } else if (current_state === "BOQ Submission") {
                fieldname = "boq_send_back_remarks";
                field_label = "BOQ Send Back Remarks";
            } else if (current_state === "Evaluation Process") {
                fieldname = "evaluation_send_back_remarks";
                field_label = "Evaluation Send Back Remarks";
            } else if (current_state === "Order Closure") {
                fieldname = "order_closure_send_back_remarks";
                field_label = "Order Closure Send Back Remarks";
            } else if (current_state === "Vendor Finalisation") {
                fieldname = "vendor_onboarding_send_back_remarks";
                field_label = "Vendor Onboarding Send Back Remarks";
            }

            if (fieldname) {
                return new Promise((resolve, reject) => {
                    frappe.dom.unfreeze();
                    let dialog = new frappe.ui.Dialog({
                        title: __("Enter {0}", [__(field_label)]),
                        fields: [
                            {
                                label: __(field_label),
                                fieldname: "remarks",
                                fieldtype: "Small Text",
                                reqd: 0
                            }
                        ],
                        primary_action_label: __("Send Back"),
                        primary_action(values) {
                            frm.set_value(fieldname, values.remarks || "");
                            frm.doc[fieldname] = values.remarks || "";
                            frm.refresh_field(fieldname);
                            dialog.primary_action_fulfilled = true;
                            dialog.hide();
                            frappe.dom.freeze();
                            frm.save().then(() => {
                                resolve();
                            });
                        },
                        on_hide() {
                            if (!dialog.primary_action_fulfilled) {
                                frappe.dom.unfreeze();
                                reject();
                            }
                        }
                    });
                    dialog.show();
                });
            }
        }
    },
    schematic_attachments_add(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, "stage", "schematic");
    },
    boq_attachments_add(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, "stage", "boq");
    },
    vendor_evaluation_attachments_add(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, "stage", "vendor evaluation");
    },
    floating_enquiries_attachments_add(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, "stage", "floating enquiries");
    },
    pre_bid_technical_meeting_attachments_add(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, "stage", "pre-bid / technical meeting");
    },
    negotiation_1_attachments_add(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, "stage", "negotiation 1");
    },
    negotiation_2_attachments_add(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, "stage", "negotiation 2");
    },
    order_approval_attachments_add(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, "stage", "order approval");
    },
    agreement_order_attachments_add(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, "stage", "agreement/order");
    },
    introduction_meeting_attachments_add(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, "stage", "introduction meeting");
    },
    mobilization_attachments_add(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, "stage", "mobilization");
    }
});

// Helper to assign a value silently (updates doc memory & field DOM without dirtying the form)
function set_field_value(frm, fieldname, value, silent=false) {
    if (silent) {
        if (frm.doc[fieldname] !== value) {
            frm.doc[fieldname] = value;
            frm.refresh_field(fieldname);
        }
    } else {
        frm.set_value(fieldname, value);
    }
}

function get_duration_left_str(target_date, work_initiation=null) {
    if (!target_date) return "";
    let comparison_date = work_initiation ? work_initiation : frappe.datetime.get_today();
    let diff = frappe.datetime.get_day_diff(target_date, comparison_date);
    if (diff > 0) {
        return diff === 1 ? "1 day left" : diff + " days left";
    } else if (diff === 0) {
        return "Due today";
    } else {
        let abs_diff = Math.abs(diff);
        return abs_diff === 1 ? "1 day delayed" : abs_diff + " days delayed";
    }
}

function get_next_working_day(date_val) {
    if (date_val) {
        return add_working_days(date_val, 1);
    }
    return null;
}

function calculate_all_dates(frm) {
    calculate_target_date(frm);
    calculate_boq_target_date(frm);
    calculate_vendor_target_date(frm);
    calculate_floating_target_date(frm);
    calculate_prebid_target_date(frm);
    calculate_q1_target_date(frm);
    calculate_q2_target_date(frm);
    calculate_order_approval_target_date(frm);
    calculate_agreement_target_date(frm);
    calculate_introduction_target_date(frm);
    calculate_mobilization_target_date(frm);
    calculate_vendor_mobilization_target_date(frm);
    update_boq_section(frm);
    update_vendor_evaluation_section(frm);
    update_introduction_section(frm);
    update_order_closure_section(frm);
    update_vendor_onboarding_section(frm);
}

function add_working_days(start_date, days) {
    let current_date = frappe.datetime.str_to_obj(start_date);
    let remaining_days = parseInt(days);
    while (remaining_days > 0) {
        current_date.setDate(current_date.getDate() + 1);
        if (current_date.getDay() !== 0) {
            remaining_days--;
        }
    }
    return frappe.datetime.obj_to_str(current_date);
}

function calculate_target_date(frm) {
    if (frm.doc.initiated_date && frm.doc.no_of_days_planned) {
        frm.set_value(
            "target_date",
            add_working_days(
                frm.doc.initiated_date,
                frm.doc.no_of_days_planned
            )
        );
    }
}

function calculate_boq_target_date(frm) {
    if (frm.doc.target_date && frm.doc.boq_submission_days_planned) {
        frm.set_value(
            "boq_submission_target_date",
            add_working_days(
                frm.doc.target_date,
                frm.doc.boq_submission_days_planned
            )
        );
    }
}

function calculate_vendor_target_date(frm) {
    if (
        frm.doc.boq_submission_target_date &&
        frm.doc.introduction_meet_days_planned
    ) {
        frm.set_value(
            "vendor_evaluation_target_date",
            add_working_days(
                frm.doc.boq_submission_target_date,
                frm.doc.introduction_meet_days_planned
            )
        );
    }
}

function calculate_floating_target_date(frm) {
    if (
        frm.doc.vendor_evaluation_target_date &&
        frm.doc.floating_enquiries_days_planned
    ) {
        frm.set_value(
            "floating_enquiries_target_date",
            add_working_days(
                frm.doc.vendor_evaluation_target_date,
                frm.doc.floating_enquiries_days_planned
            )
        );
    }
}

function calculate_prebid_target_date(frm) {
    if (
        frm.doc.floating_enquiries_target_date &&
        frm.doc.pre_bid_no_of_days_planned
    ) {
        frm.set_value(
            "pre_bid_target_date",
            add_working_days(
                frm.doc.floating_enquiries_target_date,
                frm.doc.pre_bid_no_of_days_planned
            )
        );
    }
}

function calculate_q1_target_date(frm) {
    if (
        frm.doc.pre_bid_target_date &&
        frm.doc.quotation_1_days_planned
    ) {
        frm.set_value(
            "quotation_1_target_date",
            add_working_days(
                frm.doc.pre_bid_target_date,
                frm.doc.quotation_1_days_planned
            )
        );
    }
}

function calculate_q2_target_date(frm) {
    if (
        frm.doc.quotation_1_target_date &&
        frm.doc.quotation_2_days_planned
    ) {
        frm.set_value(
            "quotation_2_target_date",
            add_working_days(
                frm.doc.quotation_1_target_date,
                frm.doc.quotation_2_days_planned
            )
        );
    }
}

function calculate_order_approval_target_date(frm) {
    if (
        frm.doc.quotation_2_target_date &&
        frm.doc.order_approval_days_planned
    ) {
        frm.set_value(
            "order_approval_target_date",
            add_working_days(
                frm.doc.quotation_2_target_date,
                frm.doc.order_approval_days_planned
            )
        );
    }
}

function calculate_agreement_target_date(frm) {
    if (
        frm.doc.order_approval_target_date &&
        frm.doc.agreement_no_of_days_planned
    ) {
        frm.set_value(
            "agreement_target_date",
            add_working_days(
                frm.doc.order_approval_target_date,
                frm.doc.agreement_no_of_days_planned
            )
        );
    }
}

function calculate_introduction_target_date(frm) {
    if (
        frm.doc.agreement_target_date &&
        frm.doc.introduction_meeting_days_planned
    ) {
        frm.set_value(
            "introduction_meet_days_plan",
            add_working_days(
                frm.doc.agreement_target_date,
                frm.doc.introduction_meeting_days_planned
            )
        );
    }
}

function calculate_mobilization_target_date(frm) {
    if (
        frm.doc.introduction_meet_days_plan &&
        frm.doc.mobilization_days_planned
    ) {
        frm.set_value(
            "mobilization_target_date",
            add_working_days(
                frm.doc.introduction_meet_days_plan,
                frm.doc.mobilization_days_planned
            )
        );
    }
}

function calculate_vendor_mobilization_target_date(frm) {
    if (
        frm.doc.introduction_meet_days_plan &&
        frm.doc.vendor_days_planned
    ) {
        frm.set_value(
            "vendor_mobilization_target_date",
            add_working_days(
                frm.doc.introduction_meet_days_plan,
                frm.doc.vendor_days_planned
            )
        );
    }
}

function get_revised_date(start_date, target_date, days) {
    if (start_date && target_date && days) {
        let start = frappe.datetime.str_to_obj(start_date);
        let target = frappe.datetime.str_to_obj(target_date);
        if (start > target) {
            return add_working_days(start_date, days);
        }
    }
    return null;
}

function update_design_sample_section(frm, silent=false) {
    set_field_value(frm, "design_sample_days_planned", frm.doc.no_of_days_planned || null, silent);
    set_field_value(frm, "design_sample_target_date", frm.doc.target_date || null, silent);
    
    let revised = get_revised_date(frm.doc.work_initiation, frm.doc.target_date, frm.doc.no_of_days_planned);
    set_field_value(frm, "revised_planned_date", revised, silent);
    
    set_field_value(frm, "duration_left", get_duration_left_str(frm.doc.design_sample_target_date, frm.doc.work_initiation), silent);
    if (frm.doc.submission_date) {
        set_field_value(frm, "submission_status", "Submitted", silent);
    } else {
        set_field_value(frm, "submission_status", "Yet to Submit", silent);
    }
}

function update_boq_section(frm, silent=false) {
    set_field_value(frm, "boq_no_of_days_planned", frm.doc.boq_submission_days_planned || null, silent);
    set_field_value(frm, "boq_target_date", frm.doc.boq_submission_target_date || null, silent);
    
    // Conditional to allow manual edits
    if (!frm.doc.boq_work_initiation && frm.doc.submission_date) {
        set_field_value(frm, "boq_work_initiation", get_next_working_day(frm.doc.submission_date), silent);
    }
    
    let revised = get_revised_date(frm.doc.boq_work_initiation, frm.doc.boq_target_date, frm.doc.boq_submission_days_planned);
    set_field_value(frm, "revised_date", revised, silent);
    
    set_field_value(frm, "boq_duration_left", get_duration_left_str(frm.doc.boq_target_date, frm.doc.boq_work_initiation), silent);
    if (frm.doc.boq_submission_date) {
        set_field_value(frm, "boq_submission_status", "Submitted", silent);
    } else {
        set_field_value(frm, "boq_submission_status", "Yet to Submit", silent);
    }
}

function update_vendor_evaluation_section(frm, silent=false) {
    set_field_value(frm, "vendor_evaluation_days_planned", frm.doc.introduction_meet_days_planned || null, silent);
    set_field_value(frm, "vendor_target_date", frm.doc.vendor_evaluation_target_date || null, silent);
    
    // Conditional to allow manual edits
    if (!frm.doc.vendor_evaluation_work_initiation && frm.doc.boq_submission_date) {
        set_field_value(frm, "vendor_evaluation_work_initiation", get_next_working_day(frm.doc.boq_submission_date), silent);
    }
    
    let revised = get_revised_date(frm.doc.vendor_evaluation_work_initiation, frm.doc.vendor_target_date, frm.doc.introduction_meet_days_planned);
    set_field_value(frm, "vendor_evaluation_revised_planned_date", revised, silent);
    
    set_field_value(frm, "vendor_evaluation_duration_left", get_duration_left_str(frm.doc.vendor_target_date, frm.doc.vendor_evaluation_work_initiation), silent);
    if (frm.doc.vendor_evaluation_submission_date) {
        set_field_value(frm, "vendor_evaluation_submission_status", "Submitted", silent);
    } else {
        set_field_value(frm, "vendor_evaluation_submission_status", "Yet to Submit", silent);
    }
}

function update_introduction_section(frm, silent=false) {
    set_field_value(frm, "introduction_days_planned", frm.doc.introduction_meeting_days_planned || null, silent);
    set_field_value(frm, "introduction_target_date", frm.doc.introduction_meet_days_plan || null, silent);
    
    // Conditional to allow manual edits
    if (!frm.doc.introduction_work_initiation && frm.doc.agreement_order_submit_date) {
        set_field_value(frm, "introduction_work_initiation", get_next_working_day(frm.doc.agreement_order_submit_date), silent);
    }
    
    let revised = get_revised_date(frm.doc.introduction_work_initiation, frm.doc.introduction_target_date, frm.doc.introduction_meeting_days_planned);
    set_field_value(frm, "introduction_revised_planned_date", revised, silent);
    
    set_field_value(frm, "introduction_duration_left", get_duration_left_str(frm.doc.introduction_target_date, frm.doc.introduction_work_initiation), silent);
    if (frm.doc.introduction_submission_date) {
        set_field_value(frm, "introduction_submission_status", "Submitted", silent);
    } else {
        set_field_value(frm, "introduction_submission_status", "Yet to Submit", silent);
    }
}

function update_order_closure_section(frm, silent=false) {
    set_field_value(frm, "floating_enquiries_no_of_days_planned", frm.doc.floating_enquiries_days_planned || null, silent);
    set_field_value(frm, "floating_enquiries_target", frm.doc.floating_enquiries_target_date || null, silent);
    set_field_value(frm, "pre_bid_technical_meeting_no_of_days_planned", frm.doc.pre_bid_no_of_days_planned || null, silent);
    set_field_value(frm, "pre_bid_technical_meeting_target_date", frm.doc.pre_bid_target_date || null, silent);
    set_field_value(frm, "negotiations_1_days_plan", frm.doc.quotation_1_days_planned || null, silent);
    set_field_value(frm, "negotiations_1_target_date", frm.doc.quotation_1_target_date || null, silent);
    set_field_value(frm, "negotiations_2_days_plan", frm.doc.quotation_2_days_planned || null, silent);
    set_field_value(frm, "negotiations_2_target_date", frm.doc.quotation_2_target_date || null, silent);
    set_field_value(frm, "order_approval_days", frm.doc.order_approval_days_planned || null, silent);
    set_field_value(frm, "order_approval_target", frm.doc.order_approval_target_date || null, silent);
    set_field_value(frm, "agreement_order_days_planned", frm.doc.agreement_no_of_days_planned || null, silent);
    set_field_value(frm, "agreement_order_target_date", frm.doc.agreement_target_date || null, silent);
    
    // Conditional to allow manual edits
    if (!frm.doc.floating_enquiries_work_initiation && frm.doc.vendor_evaluation_submission_date) {
        set_field_value(frm, "floating_enquiries_work_initiation", get_next_working_day(frm.doc.vendor_evaluation_submission_date), silent);
    }
    if (!frm.doc.pre_bid_technical_meeting_work_initiation && frm.doc.floating_enquiries_submission_date) {
        set_field_value(frm, "pre_bid_technical_meeting_work_initiation", get_next_working_day(frm.doc.floating_enquiries_submission_date), silent);
    }
    if (!frm.doc.negotiations_1_work_initiation && frm.doc.pre_bid_technical_meeting_submission_date) {
        set_field_value(frm, "negotiations_1_work_initiation", get_next_working_day(frm.doc.pre_bid_technical_meeting_submission_date), silent);
    }
    if (!frm.doc.negotiations_2_work_initiation && frm.doc.negotiations_1_submit_date) {
        set_field_value(frm, "negotiations_2_work_initiation", get_next_working_day(frm.doc.negotiations_1_submit_date), silent);
    }
    if (!frm.doc.order_approval_work_initiation && frm.doc.negotiations_2_submit_date) {
        set_field_value(frm, "order_approval_work_initiation", get_next_working_day(frm.doc.negotiations_2_submit_date), silent);
    }
    if (!frm.doc.agreement_order_work_initiation && frm.doc.order_approval_submit_date) {
        set_field_value(frm, "agreement_order_work_initiation", get_next_working_day(frm.doc.order_approval_submit_date), silent);
    }

    let float_revised = get_revised_date(frm.doc.floating_enquiries_work_initiation, frm.doc.floating_enquiries_target, frm.doc.floating_enquiries_days_planned);
    set_field_value(frm, "floating_enquiries_revised_planned_date", float_revised, silent);

    let prebid_revised = get_revised_date(frm.doc.pre_bid_technical_meeting_work_initiation, frm.doc.pre_bid_technical_meeting_target_date, frm.doc.pre_bid_no_of_days_planned);
    set_field_value(frm, "pre_bid_technical_meeting_revised_planned_date", prebid_revised, silent);

    let neg1_revised = get_revised_date(frm.doc.negotiations_1_work_initiation, frm.doc.negotiations_1_target_date, frm.doc.quotation_1_days_planned);
    set_field_value(frm, "negotiations_1_rev_plan_date", neg1_revised, silent);

    let neg2_revised = get_revised_date(frm.doc.negotiations_2_work_initiation, frm.doc.negotiations_2_target_date, frm.doc.quotation_2_days_planned);
    set_field_value(frm, "negotiations_2_rev_plan_date", neg2_revised, silent);

    let approval_revised = get_revised_date(frm.doc.order_approval_work_initiation, frm.doc.order_approval_target, frm.doc.order_approval_days_planned);
    set_field_value(frm, "order_approval_revised_date", approval_revised, silent);

    let agreement_revised = get_revised_date(frm.doc.agreement_order_work_initiation, frm.doc.agreement_order_target_date, frm.doc.agreement_no_of_days_planned);
    set_field_value(frm, "agreement_order_revised_plan_date", agreement_revised, silent);

    // Timeline Status for all Order Closure sub-stages
    set_field_value(frm, "floating_enquiries_duration_left", get_duration_left_str(frm.doc.floating_enquiries_target, frm.doc.floating_enquiries_work_initiation), silent);
    set_field_value(frm, "pre_bid_technical_meeting_duration_left", get_duration_left_str(frm.doc.pre_bid_technical_meeting_target_date, frm.doc.pre_bid_technical_meeting_work_initiation), silent);
    set_field_value(frm, "negotiations_1_duration_left", get_duration_left_str(frm.doc.negotiations_1_target_date, frm.doc.negotiations_1_work_initiation), silent);
    set_field_value(frm, "negotiations_2_duration_left", get_duration_left_str(frm.doc.negotiations_2_target_date, frm.doc.negotiations_2_work_initiation), silent);
    set_field_value(frm, "order_approval_duration_left", get_duration_left_str(frm.doc.order_approval_target, frm.doc.order_approval_work_initiation), silent);
    set_field_value(frm, "agreement_order_duration_left", get_duration_left_str(frm.doc.agreement_order_target_date, frm.doc.agreement_order_work_initiation), silent);
    
    if (frm.doc.floating_enquiries_submission_date) {
        set_field_value(frm, "floating_enquiries_submission_status", "Submitted", silent);
    } else {
        set_field_value(frm, "floating_enquiries_submission_status", "Yet to Submit", silent);
    }
    if (frm.doc.pre_bid_technical_meeting_submission_date) {
        set_field_value(frm, "pre_bid_technical_meeting_submission_status", "Submitted", silent);
    } else {
        set_field_value(frm, "pre_bid_technical_meeting_submission_status", "Yet to Submit", silent);
    }
    if (frm.doc.negotiations_1_submit_date) {
        set_field_value(frm, "negotiations_1_submit_status", "Submitted", silent);
    } else {
        set_field_value(frm, "negotiations_1_submit_status", "Yet to Submit", silent);
    }
    if (frm.doc.negotiations_2_submit_date) {
        set_field_value(frm, "negotiations_2_submit_status", "Submitted", silent);
    } else {
        set_field_value(frm, "negotiations_2_submit_status", "Yet to Submit", silent);
    }
    if (frm.doc.order_approval_submit_date) {
        set_field_value(frm, "order_approval_submit_status", "Submitted", silent);
    } else {
        set_field_value(frm, "order_approval_submit_status", "Yet to Submit", silent);
    }
    if (frm.doc.agreement_order_submit_date) {
        set_field_value(frm, "agreement_order_submission", "Submitted", silent);
    } else {
        set_field_value(frm, "agreement_order_submission", "Yet to Submit", silent);
    }
}

function update_vendor_onboarding_section(frm, silent=false) {
    set_field_value(frm, "final_vendor_name", frm.doc.finalized_vendor_name || null, silent);
    set_field_value(frm, "vendor_contact_details", frm.doc.contact_details || null, silent);
    
    // Conditional to allow manual edits
    if (!frm.doc.mobilization_work_initiation && frm.doc.introduction_submission_date) {
        set_field_value(frm, "mobilization_work_initiation", get_next_working_day(frm.doc.introduction_submission_date), silent);
    }
    
    let revised = get_revised_date(frm.doc.mobilization_work_initiation, frm.doc.mobilization_target_date, frm.doc.mobilization_days_planned);
    set_field_value(frm, "mobilization_revised_planned_date", revised, silent);
    
    set_field_value(frm, "mobilization_duration_left", get_duration_left_str(frm.doc.mobilization_target_date, frm.doc.mobilization_work_initiation), silent);
    if (frm.doc.introduction_submission_date) {
        set_field_value(frm, "introduction_submission_status", "Submitted", silent);
    } else {
        set_field_value(frm, "introduction_submission_status", "Yet to Submit", silent);
    }
    if (frm.doc.mobilization_submit_date) {
        set_field_value(frm, "mobilization_submit_status", "Submitted", silent);
    } else {
        set_field_value(frm, "mobilization_submit_status", "Yet to Submit", silent);
    }
}

frappe.ui.form.on("Tender Attachment", {
    attachment(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        const mapping = {
            "schematic_attachments": "schematic",
            "boq_attachments": "boq",
            "vendor_evaluation_attachments": "vendor evaluation",
            "floating_enquiries_attachments": "floating enquiries",
            "pre_bid_technical_meeting_attachments": "pre-bid / technical meeting",
            "negotiation_1_attachments": "negotiation 1",
            "negotiation_2_attachments": "negotiation 2",
            "order_approval_attachments": "order approval",
            "agreement_order_attachments": "agreement/order",
            "introduction_meeting_attachments": "introduction meeting",
            "mobilization_attachments": "mobilization"
        };
        if (row.parentfield && mapping[row.parentfield]) {
            frappe.model.set_value(cdt, cdn, "stage", mapping[row.parentfield]);
        }
    }
});

function update_approx_value_in_words(frm) {
    let val = frm.doc.approx_value_in_lakhs;
    if (val) {
        let amount_in_rupees = val * 100000;
        let words = num_to_words_indian(amount_in_rupees);
        if (words) {
            frm.set_df_property("approx_value_in_lakhs", "description", `<b>In Words:</b> ${words}`);
        } else {
            frm.set_df_property("approx_value_in_lakhs", "description", "");
        }
    } else {
        frm.set_df_property("approx_value_in_lakhs", "description", "");
    }
}

function convert_whole_number(num) {
    const a = [
        "", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
        "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"
    ];
    const b = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"];
    
    if (num === 0) return "Zero";
    
    function helper(n) {
        let temp = "";
        if (n < 20) {
            temp = a[n];
        } else if (n < 100) {
            temp = b[Math.floor(n / 10)] + (n % 10 !== 0 ? " " + a[n % 10] : "");
        } else {
            temp = a[Math.floor(n / 100)] + " Hundred" + (n % 100 !== 0 ? " " + helper(n % 100) : "");
        }
        return temp;
    }
    
    let result = "";
    
    // Crore (1,00,00,000)
    let crore = Math.floor(num / 10000000);
    num %= 10000000;
    if (crore > 0) {
        result += helper(crore) + " Crore ";
    }
    
    // Lakh (1,00,000)
    let lakh = Math.floor(num / 100000);
    num %= 100000;
    if (lakh > 0) {
        result += helper(lakh) + " Lakh ";
    }
    
    // Thousand (1,000)
    let thousand = Math.floor(num / 1000);
    num %= 1000;
    if (thousand > 0) {
        result += helper(thousand) + " Thousand ";
    }
    
    // Hundred and remaining
    if (num > 0) {
        result += helper(num);
    }
    
    return result.trim();
}

function num_to_words_indian(num) {
    if (isNaN(num) || num <= 0) return "";
    
    num = Math.round(num * 100) / 100;
    
    let str = num.toFixed(2);
    let parts = str.split('.');
    let whole = parseInt(parts[0]);
    let decimal = parseInt(parts[1]);
    
    let words = "";
    
    if (whole > 0 && decimal > 0) {
        words = convert_whole_number(whole) + " Rupees and " + convert_whole_number(decimal) + " Paise Only";
    } else if (whole > 0) {
        words = convert_whole_number(whole) + " Rupees Only";
    } else if (decimal > 0) {
        words = convert_whole_number(decimal) + " Paise Only";
    }
    
    return words;
}