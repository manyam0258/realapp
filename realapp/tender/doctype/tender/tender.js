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
            "introduction_meet_days_plan"
        ];

        const tab2_fields = [
            "design_sample_days_planned", "revised_planned_date", "work_initiation", 
            "submission_date", "design_sample_target_date", "duration_left", 
            "revision_status", "submission_status", "custom_attachment_1", 
            "custom_attachment_2", "custom_attachment_3", "custom_attachment_4", 
            "custom_attachment_5", "custom_attachment_6", "custom_attachment_7", 
            "custom_attachment_8"
        ];

        const tab3_fields = [
            "boq_no_of_days_planned", "revised_date", "boq_work_initiation", 
            "boq_submission_date", "boq_target_date", "boq_duration_left", 
            "boq_revision_status", "boq_submission_status", "custom_boq_attachment_1", 
            "custom_boq_attachment_2", "custom_boq_attachment_3", "custom_boq_attachment_4", 
            "custom_boq_attachment_5", "custom_boq_attachment_6", "custom_boq_attachment_7"
        ];

        const tab4_fields = [
            "vendor_evaluation_days_planned", "vendor_evaluation_revised_planned_date", 
            "vendor_evaluation_work_initiation", "vendor_evaluation_submission_date", 
            "vendor_target_date", "vendor_evaluation_duration_left", 
            "vendor_evaluation_revision_status", "vendor_evaluation_submission_status", 
            "floating_enquiries_no_of_days_planned", "floating_enquiries_revised_planned_date", 
            "floating_enquiries_work_initiation", "floating_enquiries_submission_date", 
            "floating_enquiries_target", "floating_enquiries_duration_left", 
            "floating_enquiries_revision_status", "floating_enquiries_submission_status", 
            "pre_bid_technical_meeting_no_of_days_planned", "pre_bid_technical_meeting_revised_planned_date", 
            "pre_bid_technical_meeting_work_initiation", "pre_bid_technical_meeting_submission_date", 
            "pre_bid_technical_meeting_target_date", "pre_bid_technical_meeting_duration_left", 
            "pre_bid_technical_meeting_revision_status", "pre_bid_technical_meeting_submission_status", 
            "negotiations_1_days_plan", "negotiations_1_rev_plan_date", 
            "negotiations_1_work_initiation", "negotiations_1_submit_date", 
            "negotiations_1_target_date", "negotiations_1_duration_left", 
            "negotiations_1_revision_status", "negotiations_1_submit_status", 
            "custom_attachment_negotiation_1_", "custom_attachment_negotiation_2", 
            "custom_attachment_negotiation_3", "negotiations_2_days_plan", 
            "negotiations_2_rev_plan_date", "negotiations_2_work_initiation", 
            "negotiations_2_submit_date", "negotiations_2_target_date", 
            "negotiations_2_duration_left", "negotiations_2_revision_status", 
            "negotiations_2_submit_status", "custom_attachment_1_negotiation_2", 
            "custom_attachment_2_negotiation_2", "custom_attachment_3_negotiation_2", 
            "order_approval_days", "order_approval_revised_date", "order_approval_work_initiation", 
            "order_approval_submit_date", "order_approval_target", "order_approval_duration_left", 
            "order_approval_revision_status", "order_approval_submit_status", 
            "custom_order_approval_attachment_1", "custom_order_approval_attachment_2", 
            "agreement_order_days_planned", "agreement_order_revised_plan_date", 
            "agreement_order_work_initiation", "agreement_order_submit_date", 
            "agreement_order_target_date", "agreement_order_duration_left", 
            "agreement_order_revision_status", "agreement_order_submission", 
            "custom_order_issue_attachment_1", "custom_order_issue_attachment_2", 
            "finalized_vendor_name", "contact_details"
        ];

        const tab5_fields = [
            "final_vendor_name", "vendor_contact_details", "introduction_days_planned", 
            "introduction_revised_planned_date", "introduction_work_initiation", 
            "introduction_submission_date", "introduction_target_date", "introduction_duration_left", 
            "introduction_revision_status", "introduction_submission_status", "mobilization_days_planned", 
            "mobilization_revised_planned_date", "mobilization_work_initiation", "mobilization_submit_date", 
            "mobilization_target_date", "mobilization_duration_left", "mobilization_revision_status", 
            "mobilization_submit_status"
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

        // ─── 3. CUMULATIVE ROLE-BASED VISIBILITY ───
        let show_tab1 = false;
        let show_tab2 = false;
        let show_tab3 = false;
        let show_tab4 = false;
        let show_tab5 = false;

        let edit_tab1 = false;
        let edit_tab2 = false;
        let edit_tab3 = false;
        let edit_tab4 = false;
        let edit_tab5 = false;

        const roles = frappe.user_roles || [];

        if (roles.includes("Planning") || roles.includes("System Manager")) {
            show_tab1 = true;
            show_tab5 = true;
            edit_tab1 = true;
            edit_tab5 = true;
        }
        if (roles.includes("Architect") || roles.includes("System Manager")) {
            show_tab1 = true;
            show_tab2 = true;
            edit_tab2 = true;
        }
        if (roles.includes("Quantity Surveyor") || roles.includes("System Manager")) {
            show_tab1 = true;
            show_tab3 = true;
            edit_tab3 = true;
        }
        if (roles.includes("Procurement Team") || roles.includes("System Manager")) {
            show_tab1 = true;
            show_tab4 = true;
            edit_tab4 = true;
        }

        // Apply tab visibility
        set_tab_visible("initiation_tab", show_tab1);
        set_tab_visible("schematic_readiness_tab", show_tab2);
        set_tab_visible("tab_3_tab", show_tab3);
        set_tab_visible("tab_4_tab", show_tab4);
        set_tab_visible("tab_5_tab", show_tab5);

        // Apply field states (hidden, read_only)
        set_fields_state(tab1_fields, !show_tab1, !edit_tab1);
        set_fields_state(tab2_fields, !show_tab2, !edit_tab2);
        set_fields_state(tab3_fields, !show_tab3, !edit_tab3);
        set_fields_state(tab4_fields, !show_tab4, !edit_tab4);
        set_fields_state(tab5_fields, !show_tab5, !edit_tab5);

        // ─── 4. SILENT UPDATE OF CALCULATED FIELDS ───
        // Run section updates silently to prevent setting the form dirty on load / refresh
        update_design_sample_section(frm, true);
        update_boq_section(frm, true);
        update_vendor_evaluation_section(frm, true);
        update_introduction_section(frm, true);
        update_order_closure_section(frm, true);
        update_vendor_onboarding_section(frm, true);
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
        update_boq_section(frm);
        update_vendor_evaluation_section(frm);
    },
    boq_submission_days_planned(frm) {
        calculate_all_dates(frm);
        update_boq_section(frm);
    },
    floating_enquiries_submission_date(frm) {
        update_order_closure_section(frm);
    },
    pre_bid_technical_meeting_submission_date(frm) {
        update_order_closure_section(frm);
    },
    negotiations_1_submit_date(frm) {
        update_order_closure_section(frm);
    },
    negotiations_2_submit_date(frm) {
        update_order_closure_section(frm);
    },
    order_approval_submit_date(frm) {
        update_order_closure_section(frm);
    },
    agreement_order_submit_date(frm) {
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

function update_design_sample_section(frm, silent=false) {
    set_field_value(frm, "design_sample_days_planned", frm.doc.no_of_days_planned || null, silent);
    set_field_value(frm, "design_sample_target_date", frm.doc.target_date || null, silent);
    if (
        frm.doc.work_initiation &&
        frm.doc.design_sample_target_date
    ) {
        let target_date = frappe.datetime.str_to_obj(
            frm.doc.design_sample_target_date
        );
        let work_initiation = frappe.datetime.str_to_obj(
            frm.doc.work_initiation
        );
        let diff = Math.floor(
            (target_date - work_initiation) /
            (1000 * 60 * 60 * 24)
        );
        set_field_value(frm, "duration_left", diff, silent);
    } else {
        set_field_value(frm, "duration_left", 0, silent);
    }
    if (frm.doc.submission_date) {
        set_field_value(frm, "submission_status", "Submitted", silent);
    } else {
        set_field_value(frm, "submission_status", "Yet to Submit", silent);
    }
}

function update_boq_section(frm, silent=false) {
    set_field_value(frm, "boq_no_of_days_planned", frm.doc.boq_submission_days_planned || null, silent);
    set_field_value(frm, "boq_target_date", frm.doc.boq_submission_target_date || null, silent);
    set_field_value(frm, "boq_work_initiation", frm.doc.submission_date || null, silent);
    if (
        frm.doc.submission_date &&
        frm.doc.boq_target_date
    ) {
        let target_date = frappe.datetime.str_to_obj(
            frm.doc.boq_target_date
        );
        let work_initiation = frappe.datetime.str_to_obj(
            frm.doc.submission_date
        );
        let diff = Math.floor(
            (target_date - work_initiation) /
            (1000 * 60 * 60 * 24)
        );
        set_field_value(frm, "boq_duration_left", diff, silent);
    } else {
        set_field_value(frm, "boq_duration_left", 0, silent);
    }
    if (frm.doc.boq_submission_date) {
        set_field_value(frm, "boq_submission_status", "Submitted", silent);
    } else {
        set_field_value(frm, "boq_submission_status", "Yet to Submit", silent);
    }
}

function update_vendor_evaluation_section(frm, silent=false) {
    set_field_value(frm, "vendor_evaluation_days_planned", frm.doc.introduction_meet_days_planned || null, silent);
    set_field_value(frm, "vendor_target_date", frm.doc.vendor_evaluation_target_date || null, silent);
    set_field_value(frm, "vendor_evaluation_work_initiation", frm.doc.boq_submission_date || null, silent);
    if (
        frm.doc.boq_submission_date &&
        frm.doc.vendor_evaluation_target_date
    ) {
        let target_date = frappe.datetime.str_to_obj(
            frm.doc.vendor_evaluation_target_date
        );
        let work_initiation = frappe.datetime.str_to_obj(
            frm.doc.boq_submission_date
        );
        let diff = Math.floor(
            (target_date - work_initiation) /
            (1000 * 60 * 60 * 24)
        );
        set_field_value(frm, "vendor_evaluation_duration_left", diff, silent);
    } else {
        set_field_value(frm, "vendor_evaluation_duration_left", 0, silent);
    }
    if (frm.doc.vendor_evaluation_submission_date) {
        set_field_value(frm, "vendor_evaluation_submission_status", "Submitted", silent);
    } else {
        set_field_value(frm, "vendor_evaluation_submission_status", "Yet to Submit", silent);
    }
}

function update_introduction_section(frm, silent=false) {
    set_field_value(frm, "introduction_days_planned", frm.doc.introduction_meeting_days_planned || null, silent);
    set_field_value(frm, "introduction_target_date", frm.doc.introduction_meet_days_plan || null, silent);
    set_field_value(frm, "introduction_work_initiation", frm.doc.agreement_order_submit_date || null, silent);
    if (
        frm.doc.agreement_order_submit_date &&
        frm.doc.introduction_target_date
    ) {
        let target_date = frappe.datetime.str_to_obj(
            frm.doc.introduction_target_date
        );
        let work_initiation = frappe.datetime.str_to_obj(
            frm.doc.agreement_order_submit_date
        );
        let diff = Math.floor(
            (target_date - work_initiation) /
            (1000 * 60 * 60 * 24)
        );
        set_field_value(frm, "introduction_duration_left", diff, silent);
    } else {
        set_field_value(frm, "introduction_duration_left", 0, silent);
    }
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