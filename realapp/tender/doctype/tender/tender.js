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
    introduction_submission_date(frm) {
        update_introduction_section(frm);
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
    update_boq_section(frm);
    update_vendor_evaluation_section(frm);
    update_introduction_section(frm);
    update_order_closure_section(frm);
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
        frm.set_value("duration_left", diff);
    } else {
        frm.set_value("duration_left", 0);
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
    frm.set_value(
        "boq_work_initiation",
        frm.doc.submission_date || null
    );
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
        frm.set_value("boq_duration_left", diff);
    } else {
        frm.set_value("boq_duration_left", 0);
    }
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
    frm.set_value(
        "vendor_evaluation_work_initiation",
        frm.doc.boq_submission_date || null
    );
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
        frm.set_value(
            "vendor_evaluation_duration_left",
            diff
        );
    } else {
        frm.set_value(
            "vendor_evaluation_duration_left",
            0
        );
    }
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
    frm.set_value(
        "introduction_work_initiation",
        frm.doc.agreement_order_submit_date || null
    );
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
        frm.set_value(
            "introduction_duration_left",
            diff
        );
    } else {
        frm.set_value(
            "introduction_duration_left",
            0
        );
    }
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
    frm.set_value(
        "pre_bid_technical_meeting_no_of_days_planned",
        frm.doc.pre_bid_no_of_days_planned || null
    );
    frm.set_value(
        "pre_bid_technical_meeting_target_date",
        frm.doc.pre_bid_target_date || null
    );
    frm.set_value(
        "negotiations_1_days_plan",
        frm.doc.quotation_1_days_planned || null
    );
    frm.set_value(
        "negotiations_1_target_date",
        frm.doc.quotation_1_target_date || null
    );
    frm.set_value(
        "negotiations_2_days_plan",
        frm.doc.quotation_2_days_planned || null
    );
    frm.set_value(
        "negotiations_2_target_date",
        frm.doc.quotation_2_target_date || null
    );
    frm.set_value(
        "order_approval_days",
        frm.doc.order_approval_days_planned || null
    );
    frm.set_value(
        "order_approval_target",
        frm.doc.order_approval_target_date || null
    );
    frm.set_value(
        "agreement_order_days_planned",
        frm.doc.agreement_no_of_days_planned || null
    );
    frm.set_value(
        "agreement_order_target_date",
        frm.doc.agreement_target_date || null
    );
    if (frm.doc.floating_enquiries_submission_date) {
        frm.set_value(
            "floating_enquiries_submission_status",
            "Submitted"
        );
    } else {
        frm.set_value(
            "floating_enquiries_submission_status",
            "Yet to Submit"
        );
    }
    if (frm.doc.pre_bid_technical_meeting_submission_date) {
        frm.set_value(
            "pre_bid_technical_meeting_submission_status",
            "Submitted"
        );
    } else {
        frm.set_value(
            "pre_bid_technical_meeting_submission_status",
            "Yet to Submit"
        );
    }
    if (frm.doc.negotiations_1_submit_date) {
        frm.set_value(
            "negotiations_1_submit_status",
            "Submitted"
        );
    } else {
        frm.set_value(
            "negotiations_1_submit_status",
            "Yet to Submit"
        );
    }
    if (frm.doc.negotiations_2_submit_date) {
        frm.set_value(
            "negotiations_2_submit_status",
            "Submitted"
        );
    } else {
        frm.set_value(
            "negotiations_2_submit_status",
            "Yet to Submit"
        );
    }
    if (frm.doc.order_approval_submit_date) {
        frm.set_value(
            "order_approval_submit_status",
            "Submitted"
        );
    } else {
        frm.set_value(
            "order_approval_submit_status",
            "Yet to Submit"
        );
    }

    if (frm.doc.agreement_order_submit_date) {
        frm.set_value(
            "agreement_order_submission",
            "Submitted"
        );
    } else {
        frm.set_value(
            "agreement_order_submission",
            "Yet to Submit"
        );
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
    if (frm.doc.mobilization_submit_date) {
        frm.set_value(
            "mobilization_submit_status",
            "Submitted"
        );
    } else {
        frm.set_value(
            "mobilization_submit_status",
            "Yet to Submit"
        );
    }
}