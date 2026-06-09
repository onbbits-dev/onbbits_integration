// Copyright (c) 2025, It provides complete, centralized control over WhatsApp communication inside Frappe, enabling businesses to automate customer messaging with accuracy, reliability, and real-time synchronization. and contributors
// For license information, please see license.txt

frappe.ui.form.on("OnBBits Template Trigger", {
    refresh(frm) {
        whatsapp_template_filter(frm);
        custom_buttons(frm)
        // update_message_sent_to(frm)
        mapping_field(frm)
    },
    app_name(frm) {
        whatsapp_template_filter(frm);
    },
    whatsapp_template(frm){
        whatsapp_template_filter(frm);
        fetch_template_params(frm)
    },
    reference_doctype(frm) {
        mapping_field(frm);
        update_message_sent_to(frm)
    },
    media_source(frm) {
        if (frm.doc.media_source === "Document Field") {
            update_attach(frm);
        }
        else if(frm.doc.media_source === "Print Format PDF"){
            print_format_filter(frm);
        }
    }
});

function whatsapp_template_filter(frm){
    frm.set_query("whatsapp_template", function() {
        return {
            filters: {
                app_name: frm.doc.onbbits_app_name,
                status: "APPROVED"
            }
        };
    });
}

function print_format_filter(frm){
    frm.set_query("print_format", function() {
        return {
            filters: {
                doc_type: frm.doc.reference_doctype
            }
        };
    });
}

function fetch_template_params(frm) {
    if (!frm.doc.whatsapp_template) return;
    frappe.db.get_doc("OnBBits Template", frm.doc.whatsapp_template)
        .then(template => {
            frm.clear_table("template_parameters");
            (template.template_parameters || []).forEach(param => {
                let row = frm.add_child("template_parameters");
                row.parameter = param.parameter;
            });

            frm.refresh_field("template_parameters");
        });
}

function mapping_field(frm) {
    frm.fields_dict["template_parameters"].grid.update_docfield_property(
        "reference_field",
        "options",
        []
    );
   
    if (frm.doc.reference_doctype) {
        frappe.call({
            method: "onbbits_integration.api.get_doctype_fields",
            args: {
                doctype: frm.doc.reference_doctype
            },
            callback(r) {
                console.log("r", r)
                if (r.message) {
                    frm.fields_dict["template_parameters"].grid.update_docfield_property(
                        "reference_field",
                        "options",
                        r.message.join("\n")
                    );
                }
            }
        });
    }
}

function update_message_sent_to(frm) {
    if (!frm.doc.reference_doctype) return;

    frappe.call({
        method: "onbbits_integration.api.get_phone_fields",
        args: { doctype: frm.doc.reference_doctype },
        callback(r) {
            if (r.message && r.message.length > 0) {
                // Populate Autocomplete
                frm.fields_dict.message_sent_to.set_data(r.message);
            } else {
                // No phone fields found
                frappe.msgprint({
                    title: __("No phone fields found"),
                    message: __("No phone fields exist in this Doctype. "
                        + "You can create one automatically by clicking "
                        + "the 'Auto Create Message Sent To Field' option."),
                    indicator: "orange"
                });

                // Clear existing options
                frm.fields_dict.message_sent_to.set_data([]);
            }
        }
    });
}

function update_attach(frm) {
    if (!frm.doc.reference_doctype) return;

    frappe.call({
        method: "onbbits_integration.api.get_attach_fields",
        args: { doctype: frm.doc.reference_doctype },
        callback(r) {
            if (r.message && r.message.length > 0) {
                // Populate Autocomplete
                frm.fields_dict.document_field_name.set_data(r.message);
            } else {
                frappe.msgprint({
                    title: __("No Attach Fields Found"),
                    message: __(
                        `No attach fields exist in this DocType. First create an <b>Attach</b> field in the DocType <b>${frm.doc.reference_doctype}</b> to attach documents in the message.`
                    ),
                    indicator: "orange"
                });

                // Clear existing options
                frm.fields_dict.document_field_name.set_data([]);
            }
        }
    });
}

function custom_buttons(frm){
    if (frm.doc.reference_doctype) {
        frm.add_custom_button(__('Auto Create "Message Sent To" Field'), () => {
            auto_create_msg_sent_to_field(frm);
        });
    }
}

function auto_create_msg_sent_to_field(frm) {
    if (!frm.doc.reference_doctype) {
        frappe.msgprint(__('Please select a Doctype first'));
        return;
    }

    frappe.call({
        method: "onbbits_integration.api.auto_create_msg_sent_to_field",
        args: { doctype: frm.doc.reference_doctype },
        callback(r) {
            if (r.message && r.message.success) {
                frappe.msgprint(__('Message Sent To field has been created successfully'));
                
                // Reload the phone fields in Autocomplete
                update_message_sent_to(frm);
            } else {
                frappe.msgprint(__('Failed to create field. Reason: ') + (r.message?.error || 'Unknown'));
            }
        }
    });
}

frappe.ui.form.on("Template Trigger Parameter", {
    reference_field(frm, cdt, cdn) {
        const row = frappe.get_doc(cdt, cdn);
        if (!row.reference_field) return;

        const df = frappe.meta.get_docfield(
            "Template Trigger Parameter",
            "reference_field",
            frm.doc.name
        );

        let options = (df.options || "")
            .split("\n")
            .map(v => v.trim())
            .filter(Boolean);

        if (!options.includes(row.reference_field)) {
            options.push(row.reference_field);

            frm.fields_dict["template_parameters"].grid.update_docfield_property(
                "reference_field",
                "options",
                options.join("\n")
            );
        }
    }
});
