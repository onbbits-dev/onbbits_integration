import frappe
import requests
import json
from onbbits_integration.onbbits_api import send_onbbits_template

@frappe.whitelist()
def get_doctype_fields(doctype):
    meta = frappe.get_meta(doctype)
    fields = []

    for df in meta.fields:
        # include only usable fieldtypes
        if df.fieldtype in ["Data","Phone", "Link", "Int", "Float", "Currency", "Date", "Datetime", "Small Text", "Duration", "Check", "Select", "Barcode", "Percent", "Rating", "Text", "Time"]:
            fields.append(df.fieldname)

    return fields

def validate_onbbits_event(doc, method):
    event_map = {
        "before_insert": "Insert",
        "on_update": "Update",
        "on_submit": "Submit",
        "on_cancel": "Cancel"
    }

    current_event = event_map.get(method)
    if not current_event:
        return

    # Fetch template triggers for this Doctype + Event
    triggers = frappe.get_all(
        "OnBBits Template Trigger",
        filters={
            "reference_doctype": doc.doctype,
            "event": current_event,
            "disabled": 0
        },
        fields=["name", "message_sent_to", "document_field_name"]
    )

    if not triggers:
        return  # no rules → skip

    for trg in triggers:
        sent_to_field = trg.get("message_sent_to")
        document_field = trg.get("document_field_name")

        if sent_to_field:
            if hasattr(doc, sent_to_field):
                message_sent_to = doc.get(sent_to_field)
                if not message_sent_to:
                    frappe.throw(
                        f"The field <b>{sent_to_field}</b> (Message Sent To) is mandatory "
                        f"for WhatsApp Template <b>{trg.name}</b> before <b>{current_event}</b>."
                    )

        if document_field:
            value = doc.get(document_field)

            if not value:
                frappe.throw(
                    f"The field <b>{document_field}</b> is mandatory "
                    f"for WhatsApp Template <b>{trg.name}</b> before "
                    f"<b>{current_event}</b>."
                )

        params = frappe.get_all(
            "Template Trigger Parameter",
            filters={"parent": trg.name},
            fields=["reference_field", "parameter"]
        )

        for p in params:
            fieldname = p.reference_field

            # Validate mandatory fields before event
            if hasattr(doc, fieldname):
                value = doc.get(fieldname)

                if not value:
                    frappe.throw(
                        f"Missing mandatory field <b>{fieldname}</b> required for "
                        f"WhatsApp Template (Parameter #{p.parameter}).<br>"
                        f"This field must be filled before <b>{current_event}</b>."
                    )

        send_onbbits_template(doc, trg.name)

@frappe.whitelist()
def get_phone_fields(doctype):
    meta = frappe.get_meta(doctype)
    phone_fields = []
    for df in meta.fields:
        # include only usable fieldtypes
        if df.fieldtype in ["Phone"]:
            phone_fields.append(df.fieldname)
    return phone_fields

@frappe.whitelist()
def get_attach_fields(doctype):
    meta = frappe.get_meta(doctype)
    attach_fields = []
    for df in meta.fields:
        # include only usable fieldtypes
        if df.fieldtype in ["Attach"]:
            attach_fields.append(df.fieldname)
    return attach_fields

@frappe.whitelist()
def auto_create_msg_sent_to_field(doctype):
    fieldname = "message_sent_to"
    label = "Message Sent To"

    meta = frappe.get_meta(doctype)
    if fieldname in [d.fieldname for d in meta.fields]:
        return {"success": False, "error": "Field already exists"}

    # Create the field
    frappe.get_doc({
        "doctype": "Custom Field",
        "dt": doctype,
        "fieldname": fieldname,
        "label": label,
        "fieldtype": "Phone",
        "insert_after": "naming_series",  # optional, choose placement
        "reqd": 0,
        "unique": 0,
        "module": "Onbbits Integration",
    }).insert(ignore_permissions=True)

    # Clear cache so form sees new field
    frappe.clear_cache(doctype=doctype)

    return {"success": True}