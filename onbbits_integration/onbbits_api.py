import frappe
import requests
import json
import re


@frappe.whitelist()
def sync_templates(app):
    api_url, token, app_abb = frappe.db.get_value(
        "OnBBits WA Setting",
        app,
        ["api_url", "api_key", "abbr"]
    )

    if not api_url or not token:
        frappe.throw("API URL or API Key not configured")

    url = f"{api_url.rstrip('/')}/v1/get-templates"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers, timeout=20)

    if response.status_code != 200:
        frappe.throw(response.text)

    templates = response.json()

    created, skipped = 0, 0

    for tpl in templates:
        template_name = tpl.get("name")

        if frappe.db.exists(
            "OnBBits Template",
            {
                "template_name": template_name,
                "app_name": app
            }
        ):
            skipped += 1
            continue

        body = tpl.get("body") or {}
        footer = tpl.get("footer") or {}
        header = tpl.get("header")

        # FILTER
        if header is not None and header.get("format") != "TEXT":
            skipped += 1
            continue

        header_type = None
        header_text = None

        if header:
            header_type = header.get("format")
            if header_type == "TEXT":
                header_text = header.get("text")

        # header_type = header.get("format")
        # header_text = header.get("text") if header_type == "TEXT" else None

        parameters = tpl.get("parameters", {})

        header_parameter = None
        header_params = parameters.get("header", [])

        if header_params:
            # Rule: Header can have ONLY ONE parameter
            header_parameter = header_params[0].get("example")

        doc = frappe.get_doc({
            "doctype": "OnBBits Template",
            "app_name": app,
            "template_name": template_name,
            "source": "OnBBits",
            "category": tpl.get("category", ""),
            "language": tpl.get("language", "en_US"),
            "status": "Approved" if tpl.get("metaStatus") == "APPROVED" else "Pending",
            "format": tpl.get("parameterFormat", "POSITIONAL"),
            "template_type": header_type,
            "header_text": header_text,
            "header_parameter": header_parameter, 
            "body_text": body.get("text"),
            "footer_text": footer.get("text"),
        })

        # -----------------------------
        # PARAMETERS (BODY)
        # -----------------------------

        # BODY parameters
        parameters = tpl.get("parameters", {})
        body_params = parameters.get("body", [])

        if tpl.get("parameterFormat") == "NAMED":
            for p in body_params:
                doc.append("template_parameters", {
                    "parameter": p.get("name"),
                    "value": p.get("example")
                })
        else:
            for idx, p in enumerate(body_params, start=1):
                doc.append("template_parameters", {
                    "parameter": f"{{{{{idx}}}}}",
                    "value": p.get("example")   # ✅ ALWAYS example
                })


        # -----------------------------
        # BUTTONS
        # -----------------------------
        for btn in tpl.get("buttons", []):
            doc.append("template_buttons", {
                "button_type": btn.get("type"),
                "button_text": btn.get("text"),
                "url": btn.get("url"),
                "phone_number": btn.get("phone_number")
            })

        doc.insert(ignore_permissions=True)
        doc.submit()

        created += 1

    frappe.db.commit()

    return {
        "total": len(templates),
        "created": created,
        "skipped": skipped
    }

def create_template_in_onbbits(doc):
    url = f"{doc.api_url.rstrip('/')}/v1/create-templates"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {doc.api_key}"
    }

    payload = build_template_payload(doc)

    response = requests.post(
        url,
        headers=headers,
        data=json.dumps(payload)
    )
    frappe.log_error(response.text)

    if response.status_code not in (200, 201):
        frappe.throw(response.text)
    else:
        templates_id = response.json().get("id")
        submit_url = f"{doc.api_url.rstrip('/')}/v1/{templates_id}/submit-template"
        frappe.log_error("submit response", submit_url)
        sub_res = requests.post(
            submit_url,
            headers=headers,
            data=json.dumps(payload)
        )
        frappe.log_error("sub_res",sub_res.text)
    return response.json()

def build_template_payload(doc):
    components = []

    # ---------------- HEADER ----------------

    if doc.template_type:
        components.append({
            "type": "HEADER",
            "format": doc.template_type,
            "text": doc.header_text,
            "example": {
                "header_text": [
                    doc.header_parameter
                ]
            }
        })

    # ---------------- BODY ----------------
    body_example = []
    if doc.template_parameters:
        body_example = [p.value for p in doc.template_parameters]

    components.append({
        "type": "BODY",
        "text": doc.body_text,
        "example": {
            "body_text": [body_example]
        }
    })

    # ---------------- BUTTONS ----------------
    if doc.template_buttons:
        buttons = []

        for btn in doc.template_buttons:
            button = {
                "type": btn.button_type,
                "text": btn.button_text
            }

            if btn.button_type == "URL":
                button["url"] = btn.url

            elif btn.button_type == "PHONE_NUMBER":
                button["phone_number"] = btn.phone_number
                buttons.append(button)

        components.append({
            "type": "BUTTONS",
            "buttons": buttons
        })

    return {
        "name": doc.template_name,
        "language": doc.language,
        "category": doc.category.upper(),
        "parameter_format": doc.format.upper(),
        "components": components
    }

@frappe.whitelist()
def sync_template_status():
    settings = frappe.get_all(
        "OnBBits WA Setting",
        fields=["name", "api_url", "api_key"]
    )

    for setting in settings:
        sync_status_for_app(setting)

def sync_status_for_app(setting):
    api_url = setting.api_url
    token = setting.api_key
    app_name = setting.name

    if not api_url or not token:
        return

    url = f"{api_url.rstrip('/')}/v1/templates"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        frappe.log_error(response.text, "OnBBits Template Status Sync Failed")
        return

    api_templates = response.json()

    # 🔹 Build API lookup map
    api_status_map = {
        tpl.get("name"): tpl.get("metaStatus")
        for tpl in api_templates
        if tpl.get("metaStatus")
    }

    # 🔹 Fetch only SUBMITTED + PENDING templates
    erp_templates = frappe.get_all(
        "OnBBits Template",
        filters={
            "app_name": app_name,
            "docstatus": 1,
            "status": "Pending"
        },
        fields=["name", "template_name"]
    )

    for tpl in erp_templates:
        api_status = api_status_map.get(tpl.template_name)

        if not api_status:
            continue

        # ✔ Direct assignment (NO mapping)
        frappe.db.set_value(
            "OnBBits Template",
            tpl.name,
            "status",
            api_status
        )

def send_onbbits_template(doc, trigger_name):
    # -----------------------------
    # Get Trigger
    # -----------------------------
    trigger = frappe.get_doc("OnBBits Template Trigger", trigger_name)

    wa_setting = frappe.get_doc("OnBBits WA Setting", trigger.onbbits_app_name)

    url = f"{wa_setting.api_url.rstrip('/')}/v1/send-template"

    headers = {
        "Content-Type": "application/json",
        "token": wa_setting.api_key
    }

    # -----------------------------
    # Receiver Number
    # -----------------------------
    number = doc.get(trigger.message_sent_to)
    format_number = re.sub(r"\D", "", str(number))
    if not number:
        return

    # -----------------------------
    # Build Parameters
    # -----------------------------
    parameters = []

    trigger_params = frappe.get_all(
        "Template Trigger Parameter",
        filters={"parent": trigger.name},
        fields=["reference_field","static_value", "parameter"],
        order_by="parameter asc"
    )

    for p in trigger_params:
        value = p.static_value or doc.get(p.reference_field) or None
        parameters.append({
            "type": "text",
            "text": str(value)
        })

    payload = {
        "name": format_number,
        "number": format_number,
        "template_name": trigger.template_name,
        "template_language": trigger.language or "en_US",
        "components": [
            {
                "type": "body",
                "parameters": parameters
            }
        ]
    }

    # -----------------------------
    # Send API Request
    # -----------------------------
    response = requests.post(
        url,
        headers=headers,
        data=json.dumps(payload)
    )

    frappe.log_error(
        title="OnBBits Send Template",
        message=response.text
    )

    if response.status_code not in (200, 201):
        frappe.throw(response.text)

    return response.json()