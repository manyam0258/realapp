// Copyright (c) 2026, surendhranath and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tender", {
    refresh(frm) {
        update_design_sample_section(frm);
        update_boq_section(frm);
        update_vendor_evaluation_section(frm);
        update_introduction_section(frm);
        update_order_closure_section(frm);
        update_vendor_onboarding_section(frm);
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
    custom_work_category(frm) {
        if (frm.doc.custom_work_category !== "Others") {
            frm.set_value("work_category_others", "");
        }
    },
    before_workflow_action(frm) {
        let action = frm.selected_workflow_action;
        let today = frappe.datetime.get_today();
        if (action === "Submit Design") {
            frm.set_value("submission_date", today);
        } else if (action === "Submit BOQ") {
            frm.set_value("boq_submission_date", today);
        } else if (action === "Submit Order Closure") {
            frm.set_value("vendor_evaluation_submission_date", today);
            frm.set_value("floating_enquiries_submission_date", today);
            frm.set_value("pre_bid_technical_meeting_submission_date", today);
            frm.set_value("negotiations_1_submit_date", today);
            frm.set_value("negotiations_2_submit_date", today);
            frm.set_value("order_approval_submit_date", today);
            frm.set_value("agreement_order_submit_date", today);
        } else if (action === "Submit for Vendor Onboarding" || action === "Vendor Onboarded") {
            frm.set_value("introduction_submission_date", today);
            frm.set_value("mobilization_submit_date", today);
        } else if (action === "Send Back") {
            let current_state = frm.doc.workflow_state;
            let fieldname = null;
            let field_label = "";
            let revision_field = null;
            
            if (current_state === "Design Sample / Drawings") {
                fieldname = "send_back_remarks";
                field_label = "Send Back Remarks";
                revision_field = "revision_status";
            } else if (current_state === "BOQ Submission") {
                fieldname = "boq_send_back_remarks";
                field_label = "BOQ Send Back Remarks";
                revision_field = "boq_revision_status";
            } else if (current_state === "Order Closure") {
                fieldname = "order_closure_send_back_remarks";
                field_label = "Order Closure Send Back Remarks";
                revision_field = "vendor_evaluation_revision_status";
            } else if (current_state === "Vendor Finalisation") {
                fieldname = "vendor_onboarding_send_back_remarks";
                field_label = "Vendor Onboarding Send Back Remarks";
                revision_field = "introduction_revision_status";
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
                            // Set the remarks and revision fields
                            frm.set_value(fieldname, values.remarks || "");
                            frm.doc[fieldname] = values.remarks || "";
                            frm.refresh_field(fieldname);
                            // Increment revision status
                            if (revision_field) {
                                let current_status = frm.doc[revision_field] || "R0";
                                let revision_levels = ["R0", "R1", "R2", "R3", "R4"];
                                let current_idx = revision_levels.indexOf(current_status);
                                if (current_idx < revision_levels.length - 1) {
                                    frm.set_value(revision_field, revision_levels[current_idx + 1]);
                                    frm.doc[revision_field] = revision_levels[current_idx + 1];
                                    frm.refresh_field(revision_field);
                                }
                            }
                            dialog.primary_action_fulfilled = true;
                            frappe.dom.freeze();
                            // CRITICAL: Save the document before workflow transition
                            // because apply_workflow() calls load_from_db() which would
                            // otherwise lose the remarks we just entered
                            frm.save().then(() => {
                                dialog.hide();
                                frappe.dom.freeze();
                                resolve();
                            }).catch((err) => {
                                frappe.dom.unfreeze();
                                reject(err);
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
    after_workflow_action(frm) {
        // Refresh form after workflow action to show saved send back remarks
        frm.reload();
    },
    introduction_submission_date(frm) {
        update_introduction_section(frm);
        update_vendor_onboarding_section(frm);
    },
    mobilization_submit_date(frm) {
        update_vendor_onboarding_section(frm);
    },
    mobilization_days_planned(frm) {
        calculate_all_dates(frm);
    },
    no_of_days_planned(frm) {
        calculate_all_dates(frm);
        update_design_sample_section(frm);
    },
    work_initiation(frm) {
	        update_design_sample_section(frm);
	        update_revised_design_sample_target_date(frm);
	    },
    boq_work_initiation(frm) {
        update_boq_section(frm);
        update_revised_boq_target_date(frm);
    },
    vendor_evaluation_work_initiation(frm) {
        update_vendor_evaluation_section(frm);
        update_revised_vendor_evaluation_target_date(frm);
    },
    floating_enquiries_work_initiation(frm) {
        update_order_closure_section(frm);
        update_revised_floating_enquiries_target_date(frm);
    },
    pre_bid_technical_meeting_work_initiation(frm) {
        update_order_closure_section(frm);
        update_revised_prebid_target_date(frm);
    },
    negotiations_1_work_initiation(frm) {
        update_order_closure_section(frm);
        update_revised_q1_target_date(frm);
    },
    negotiations_2_work_initiation(frm) {
        update_order_closure_section(frm);
        update_revised_q2_target_date(frm);
    },
    order_approval_work_initiation(frm) {
        update_order_closure_section(frm);
        update_revised_order_approval_target_date(frm);
    },
    agreement_order_work_initiation(frm) {
        update_order_closure_section(frm);
        update_revised_agreement_target_date(frm);
    },
    introduction_work_initiation(frm) {
        update_introduction_section(frm);
        update_revised_introduction_target_date(frm);
    },
    mobilization_work_initiation(frm) {
        update_vendor_onboarding_section(frm);
    },
    submission_date(frm) {
        frm.set_value("boq_work_initiation", frm.doc.submission_date || null);
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
        frm.set_value("vendor_evaluation_work_initiation", frm.doc.boq_submission_date || null);
        update_boq_section(frm);
        update_vendor_evaluation_section(frm);
    },
    boq_submission_days_planned(frm) {
        calculate_all_dates(frm);
        update_boq_section(frm);
    },
    vendor_evaluation_submission_date(frm) {
        frm.set_value("floating_enquiries_work_initiation", frm.doc.vendor_evaluation_submission_date || null);
        update_vendor_evaluation_section(frm);
        update_order_closure_section(frm);
    },
    floating_enquiries_submission_date(frm) {
        frm.set_value("pre_bid_technical_meeting_work_initiation", frm.doc.floating_enquiries_submission_date || null);
        update_order_closure_section(frm);
    },
    pre_bid_technical_meeting_submission_date(frm) {
        frm.set_value("negotiations_1_work_initiation", frm.doc.pre_bid_technical_meeting_submission_date || null);
        update_order_closure_section(frm);
    },
    negotiations_1_submit_date(frm) {
        frm.set_value("negotiations_2_work_initiation", frm.doc.negotiations_1_submit_date || null);
        update_order_closure_section(frm);
    },
    negotiations_2_submit_date(frm) {
        frm.set_value("order_approval_work_initiation", frm.doc.negotiations_2_submit_date || null);
        update_order_closure_section(frm);
    },
    order_approval_submit_date(frm) {
        frm.set_value("agreement_order_work_initiation", frm.doc.order_approval_submit_date || null);
        update_order_closure_section(frm);
    },
    agreement_order_submit_date(frm) {
        frm.set_value("introduction_work_initiation", frm.doc.agreement_order_submit_date || null);
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
    update_boq_section(frm);
    update_vendor_evaluation_section(frm);
    update_introduction_section(frm);
    update_order_closure_section(frm);
    update_vendor_onboarding_section(frm);
}

function get_duration_left(target_date_str, work_initiation_str) {
    if (target_date_str && work_initiation_str) {
        let target_date = frappe.datetime.str_to_obj(target_date_str);
        let work_initiation = frappe.datetime.str_to_obj(work_initiation_str);
        let diff = Math.floor((target_date - work_initiation) / (1000 * 60 * 60 * 24));
        if (diff >= 0) {
            return diff === 1 ? "1 day left" : `${diff} days left`;
        } else {
            let abs_diff = Math.abs(diff);
            return abs_diff === 1 ? "1 day delayed" : `${abs_diff} days delayed`;
        }
    }
    return "0 days left";
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

function update_design_sample_section(frm) {
    frm.set_value(
        "design_sample_days_planned",
        frm.doc.no_of_days_planned || null
    );
    frm.set_value(
        "design_sample_target_date",
        frm.doc.target_date || null
    );
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
        if (diff >= 0) {
            frm.set_value("duration_left", diff === 1 ? "1 day left" : `${diff} days left`);
        } else {
            let abs_diff = Math.abs(diff);
            frm.set_value("duration_left", abs_diff === 1 ? "1 day delayed" : `${abs_diff} days delayed`);
        }
    } else {
        frm.set_value("duration_left", "0 days left");
    }
    if (frm.doc.submission_date) {
        frm.set_value("submission_status", "Submitted");
    } else {
        frm.set_value("submission_status", "Yet to Submit");
    }
}

function update_boq_section(frm) {
    frm.set_value(
        "boq_no_of_days_planned",
        frm.doc.boq_submission_days_planned || null
    );
    frm.set_value(
        "boq_target_date",
        frm.doc.boq_submission_target_date || null
    );
    if (!frm.doc.boq_work_initiation && frm.doc.submission_date) {
        frm.set_value("boq_work_initiation", frm.doc.submission_date);
    }
    frm.set_value("boq_duration_left", get_duration_left(frm.doc.boq_target_date, frm.doc.boq_work_initiation));
    if (frm.doc.boq_submission_date) {
        frm.set_value("boq_submission_status", "Submitted");
    } else {
        frm.set_value("boq_submission_status", "Yet to Submit");
    }
}

function update_vendor_evaluation_section(frm) {
    frm.set_value(
        "vendor_evaluation_days_planned",
        frm.doc.introduction_meet_days_planned || null
    );
    frm.set_value(
        "vendor_target_date",
        frm.doc.vendor_evaluation_target_date || null
    );
    if (!frm.doc.vendor_evaluation_work_initiation && frm.doc.boq_submission_date) {
        frm.set_value("vendor_evaluation_work_initiation", frm.doc.boq_submission_date);
    }
    frm.set_value("vendor_evaluation_duration_left", get_duration_left(frm.doc.vendor_target_date, frm.doc.vendor_evaluation_work_initiation));
    if (frm.doc.vendor_evaluation_submission_date) {
        frm.set_value(
            "vendor_evaluation_submission_status",
            "Submitted"
        );
    } else {
        frm.set_value(
            "vendor_evaluation_submission_status",
            "Yet to Submit"
        );
    }
}

function update_introduction_section(frm) {
    frm.set_value(
        "introduction_days_planned",
        frm.doc.introduction_meeting_days_planned || null
    );
    frm.set_value(
        "introduction_target_date",
        frm.doc.introduction_meet_days_plan || null
    );
    if (!frm.doc.introduction_work_initiation && frm.doc.agreement_order_submit_date) {
        frm.set_value("introduction_work_initiation", frm.doc.agreement_order_submit_date);
    }
    frm.set_value("introduction_duration_left", get_duration_left(frm.doc.introduction_target_date, frm.doc.introduction_work_initiation));
    if (frm.doc.introduction_submission_date) {
        frm.set_value(
            "introduction_submission_status",
            "Submitted"
        );
    } else {
        frm.set_value(
            "introduction_submission_status",
            "Yet to Submit"
        );
    }
}

function update_order_closure_section(frm) {
    frm.set_value(
        "floating_enquiries_no_of_days_planned",
        frm.doc.floating_enquiries_days_planned || null
    );
    frm.set_value(
        "floating_enquiries_target",
        frm.doc.floating_enquiries_target_date || null
    );
    if (!frm.doc.floating_enquiries_work_initiation && frm.doc.vendor_evaluation_submission_date) {
        frm.set_value("floating_enquiries_work_initiation", frm.doc.vendor_evaluation_submission_date);
    }
    frm.set_value(
        "floating_enquiries_duration_left",
        get_duration_left(frm.doc.floating_enquiries_target, frm.doc.floating_enquiries_work_initiation)
    );

    frm.set_value(
        "pre_bid_technical_meeting_no_of_days_planned",
        frm.doc.pre_bid_no_of_days_planned || null
    );
    frm.set_value(
        "pre_bid_technical_meeting_target_date",
        frm.doc.pre_bid_target_date || null
    );
    if (!frm.doc.pre_bid_technical_meeting_work_initiation && frm.doc.floating_enquiries_submission_date) {
        frm.set_value("pre_bid_technical_meeting_work_initiation", frm.doc.floating_enquiries_submission_date);
    }
    frm.set_value(
        "pre_bid_technical_meeting_duration_left",
        get_duration_left(frm.doc.pre_bid_technical_meeting_target_date, frm.doc.pre_bid_technical_meeting_work_initiation)
    );

    frm.set_value(
        "negotiations_1_days_plan",
        frm.doc.quotation_1_days_planned || null
    );
    frm.set_value(
        "negotiations_1_target_date",
        frm.doc.quotation_1_target_date || null
    );
    if (!frm.doc.negotiations_1_work_initiation && frm.doc.pre_bid_technical_meeting_submission_date) {
        frm.set_value("negotiations_1_work_initiation", frm.doc.pre_bid_technical_meeting_submission_date);
    }
    frm.set_value(
        "negotiations_1_duration_left",
        get_duration_left(frm.doc.negotiations_1_target_date, frm.doc.negotiations_1_work_initiation)
    );

    frm.set_value(
        "negotiations_2_days_plan",
        frm.doc.quotation_2_days_planned || null
    );
    frm.set_value(
        "negotiations_2_target_date",
        frm.doc.quotation_2_target_date || null
    );
    if (!frm.doc.negotiations_2_work_initiation && frm.doc.negotiations_1_submit_date) {
        frm.set_value("negotiations_2_work_initiation", frm.doc.negotiations_1_submit_date);
    }
    frm.set_value(
        "negotiations_2_duration_left",
        get_duration_left(frm.doc.negotiations_2_target_date, frm.doc.negotiations_2_work_initiation)
    );

    frm.set_value(
        "order_approval_days",
        frm.doc.order_approval_days_planned || null
    );
    frm.set_value(
        "order_approval_target",
        frm.doc.order_approval_target_date || null
    );
    if (!frm.doc.order_approval_work_initiation && frm.doc.negotiations_2_submit_date) {
        frm.set_value("order_approval_work_initiation", frm.doc.negotiations_2_submit_date);
    }
    frm.set_value(
        "order_approval_duration_left",
        get_duration_left(frm.doc.order_approval_target, frm.doc.order_approval_work_initiation)
    );

    frm.set_value(
        "agreement_order_days_planned",
        frm.doc.agreement_no_of_days_planned || null
    );
    frm.set_value(
        "agreement_order_target_date",
        frm.doc.agreement_target_date || null
    );
    if (!frm.doc.agreement_order_work_initiation && frm.doc.order_approval_submit_date) {
        frm.set_value("agreement_order_work_initiation", frm.doc.order_approval_submit_date);
    }
    frm.set_value(
        "agreement_order_duration_left",
        get_duration_left(frm.doc.agreement_order_target_date, frm.doc.agreement_order_work_initiation)
    );

    if (frm.doc.floating_enquiries_submission_date) {
        frm.set_value("floating_enquiries_submission_status", "Submitted");
    } else {
        frm.set_value("floating_enquiries_submission_status", "Yet to Submit");
    }
    if (frm.doc.pre_bid_technical_meeting_submission_date) {
        frm.set_value("pre_bid_technical_meeting_submission_status", "Submitted");
    } else {
        frm.set_value("pre_bid_technical_meeting_submission_status", "Yet to Submit");
    }
    if (frm.doc.negotiations_1_submit_date) {
        frm.set_value("negotiations_1_submit_status", "Submitted");
    } else {
        frm.set_value("negotiations_1_submit_status", "Yet to Submit");
    }
    if (frm.doc.negotiations_2_submit_date) {
        frm.set_value("negotiations_2_submit_status", "Submitted");
    } else {
        frm.set_value("negotiations_2_submit_status", "Yet to Submit");
    }
    if (frm.doc.order_approval_submit_date) {
        frm.set_value("order_approval_submit_status", "Submitted");
    } else {
        frm.set_value("order_approval_submit_status", "Yet to Submit");
    }
    if (frm.doc.agreement_order_submit_date) {
        frm.set_value("agreement_order_submission", "Submitted");
    } else {
        frm.set_value("agreement_order_submission", "Yet to Submit");
    }
}

function update_vendor_onboarding_section(frm) {
    frm.set_value(
        "final_vendor_name",
        frm.doc.finalized_vendor_name || null
    );
    frm.set_value(
        "vendor_contact_details",
        frm.doc.contact_details || null
    );
    if (!frm.doc.mobilization_work_initiation && frm.doc.introduction_submission_date) {
        frm.set_value("mobilization_work_initiation", frm.doc.introduction_submission_date);
    }
    frm.set_value(
        "mobilization_duration_left",
        get_duration_left(frm.doc.mobilization_target_date, frm.doc.mobilization_work_initiation)
    );

    if (frm.doc.introduction_submission_date) {
        frm.set_value("introduction_submission_status", "Submitted");
    } else {
        frm.set_value("introduction_submission_status", "Yet to Submit");
    }
    if (frm.doc.mobilization_submit_date) {
        frm.set_value("mobilization_submit_status", "Submitted");
    } else {
        frm.set_value("mobilization_submit_status", "Yet to Submit");
    }
}
// Revised Target Date Calculation Functions
function update_revised_design_sample_target_date(frm) {
    if (frm.doc.work_initiation && frm.doc.no_of_days_planned && frm.doc.target_date) {
        let work_date = frappe.datetime.str_to_obj(frm.doc.work_initiation);
        let target_date = frappe.datetime.str_to_obj(frm.doc.target_date);
        
        if (work_date <= target_date) {
            // If work initiation hasn't exceeded target, revised date equals target date
            frm.set_value("revised_planned_date", frm.doc.target_date);
        } else {
            // If work initiation exceeds target, calculate revised date from work_initiation
            frm.set_value(
                "revised_planned_date",
                add_working_days(
                    frm.doc.work_initiation,
                    frm.doc.no_of_days_planned
                )
            );
        }
    }
}

function update_revised_boq_target_date(frm) {
    if (frm.doc.boq_work_initiation && frm.doc.boq_submission_days_planned && frm.doc.boq_target_date) {
        let work_date = frappe.datetime.str_to_obj(frm.doc.boq_work_initiation);
        let target_date = frappe.datetime.str_to_obj(frm.doc.boq_target_date);
        
        if (work_date <= target_date) {
            frm.set_value("revised_date", frm.doc.boq_target_date);
        } else {
            frm.set_value(
                "revised_date",
                add_working_days(
                    frm.doc.boq_work_initiation,
                    frm.doc.boq_submission_days_planned
                )
            );
        }
    }
}

function update_revised_vendor_evaluation_target_date(frm) {
    if (frm.doc.vendor_evaluation_work_initiation && frm.doc.introduction_meet_days_planned && frm.doc.vendor_target_date) {
        let work_date = frappe.datetime.str_to_obj(frm.doc.vendor_evaluation_work_initiation);
        let target_date = frappe.datetime.str_to_obj(frm.doc.vendor_target_date);
        
        if (work_date <= target_date) {
            frm.set_value("vendor_evaluation_revised_planned_date", frm.doc.vendor_target_date);
        } else {
            frm.set_value(
                "vendor_evaluation_revised_planned_date",
                add_working_days(
                    frm.doc.vendor_evaluation_work_initiation,
                    frm.doc.introduction_meet_days_planned
                )
            );
        }
    }
}

function update_revised_floating_enquiries_target_date(frm) {
    if (frm.doc.floating_enquiries_work_initiation && frm.doc.floating_enquiries_days_planned && frm.doc.floating_enquiries_target) {
        let work_date = frappe.datetime.str_to_obj(frm.doc.floating_enquiries_work_initiation);
        let target_date = frappe.datetime.str_to_obj(frm.doc.floating_enquiries_target);
        
        if (work_date <= target_date) {
            frm.set_value("floating_enquiries_revised_planned_date", frm.doc.floating_enquiries_target);
        } else {
            frm.set_value(
                "floating_enquiries_revised_planned_date",
                add_working_days(
                    frm.doc.floating_enquiries_work_initiation,
                    frm.doc.floating_enquiries_days_planned
                )
            );
        }
    }
}

function update_revised_prebid_target_date(frm) {
    if (frm.doc.pre_bid_technical_meeting_work_initiation && frm.doc.pre_bid_no_of_days_planned && frm.doc.pre_bid_technical_meeting_target_date) {
        let work_date = frappe.datetime.str_to_obj(frm.doc.pre_bid_technical_meeting_work_initiation);
        let target_date = frappe.datetime.str_to_obj(frm.doc.pre_bid_technical_meeting_target_date);
        
        if (work_date <= target_date) {
            frm.set_value("pre_bid_technical_meeting_revised_planned_date", frm.doc.pre_bid_technical_meeting_target_date);
        } else {
            frm.set_value(
                "pre_bid_technical_meeting_revised_planned_date",
                add_working_days(
                    frm.doc.pre_bid_technical_meeting_work_initiation,
                    frm.doc.pre_bid_no_of_days_planned
                )
            );
        }
    }
}

function update_revised_q1_target_date(frm) {
    if (frm.doc.negotiations_1_work_initiation && frm.doc.quotation_1_days_planned && frm.doc.negotiations_1_target_date) {
        let work_date = frappe.datetime.str_to_obj(frm.doc.negotiations_1_work_initiation);
        let target_date = frappe.datetime.str_to_obj(frm.doc.negotiations_1_target_date);
        
        if (work_date <= target_date) {
            frm.set_value("negotiations_1_rev_plan_date", frm.doc.negotiations_1_target_date);
        } else {
            frm.set_value(
                "negotiations_1_rev_plan_date",
                add_working_days(
                    frm.doc.negotiations_1_work_initiation,
                    frm.doc.quotation_1_days_planned
                )
            );
        }
    }
}

function update_revised_q2_target_date(frm) {
    if (frm.doc.negotiations_2_work_initiation && frm.doc.quotation_2_days_planned && frm.doc.negotiations_2_target_date) {
        let work_date = frappe.datetime.str_to_obj(frm.doc.negotiations_2_work_initiation);
        let target_date = frappe.datetime.str_to_obj(frm.doc.negotiations_2_target_date);
        
        if (work_date <= target_date) {
            frm.set_value("negotiations_2_rev_plan_date", frm.doc.negotiations_2_target_date);
        } else {
            frm.set_value(
                "negotiations_2_rev_plan_date",
                add_working_days(
                    frm.doc.negotiations_2_work_initiation,
                    frm.doc.quotation_2_days_planned
                )
            );
        }
    }
}

function update_revised_order_approval_target_date(frm) {
    if (frm.doc.order_approval_work_initiation && frm.doc.order_approval_days_planned && frm.doc.order_approval_target) {
        let work_date = frappe.datetime.str_to_obj(frm.doc.order_approval_work_initiation);
        let target_date = frappe.datetime.str_to_obj(frm.doc.order_approval_target);
        
        if (work_date <= target_date) {
            frm.set_value("order_approval_revised_date", frm.doc.order_approval_target);
        } else {
            frm.set_value(
                "order_approval_revised_date",
                add_working_days(
                    frm.doc.order_approval_work_initiation,
                    frm.doc.order_approval_days_planned
                )
            );
        }
    }
}

function update_revised_agreement_target_date(frm) {
    if (frm.doc.agreement_order_work_initiation && frm.doc.agreement_no_of_days_planned && frm.doc.agreement_order_target_date) {
        let work_date = frappe.datetime.str_to_obj(frm.doc.agreement_order_work_initiation);
        let target_date = frappe.datetime.str_to_obj(frm.doc.agreement_order_target_date);
        
        if (work_date <= target_date) {
            frm.set_value("agreement_order_revised_plan_date", frm.doc.agreement_order_target_date);
        } else {
            frm.set_value(
                "agreement_order_revised_plan_date",
                add_working_days(
                    frm.doc.agreement_order_work_initiation,
                    frm.doc.agreement_no_of_days_planned
                )
            );
        }
    }
}

function update_revised_introduction_target_date(frm) {
    if (frm.doc.introduction_work_initiation && frm.doc.introduction_meeting_days_planned && frm.doc.introduction_target_date) {
        let work_date = frappe.datetime.str_to_obj(frm.doc.introduction_work_initiation);
        let target_date = frappe.datetime.str_to_obj(frm.doc.introduction_target_date);
        
        if (work_date <= target_date) {
            frm.set_value("introduction_revised_planned_date", frm.doc.introduction_target_date);
        } else {
            frm.set_value(
                "introduction_revised_planned_date",
                add_working_days(
                    frm.doc.introduction_work_initiation,
                    frm.doc.introduction_meeting_days_planned
                )
            );
        }
    }
}

function update_revised_mobilization_target_date(frm) {
    if (frm.doc.mobilization_work_initiation && frm.doc.mobilization_days_planned && frm.doc.mobilization_target_date) {
        let work_date = frappe.datetime.str_to_obj(frm.doc.mobilization_work_initiation);
        let target_date = frappe.datetime.str_to_obj(frm.doc.mobilization_target_date);
        
        if (work_date <= target_date) {
            frm.set_value("mobilization_revised_planned_date", frm.doc.mobilization_target_date);
        } else {
            frm.set_value(
                "mobilization_revised_planned_date",
                add_working_days(
                    frm.doc.mobilization_work_initiation,
                    frm.doc.mobilization_days_planned
                )
            );
        }
    }
}

function update_all_revised_dates(frm) {
    update_revised_design_sample_target_date(frm);
    update_revised_boq_target_date(frm);
    update_revised_vendor_evaluation_target_date(frm);
    update_revised_floating_enquiries_target_date(frm);
    update_revised_prebid_target_date(frm);
    update_revised_q1_target_date(frm);
    update_revised_q2_target_date(frm);
    update_revised_order_approval_target_date(frm);
    update_revised_agreement_target_date(frm);
    update_revised_introduction_target_date(frm);
    update_revised_mobilization_target_date(frm);
}
