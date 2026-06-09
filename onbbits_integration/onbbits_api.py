import frappe
import requests
import json
import re
from frappe.utils import get_url


# @frappe.whitelist()
# def sync_templates(app):
#     api_url, token, app_abb = frappe.db.get_value(
#         "OnBBits WA Setting",
#         app,
#         ["api_url", "api_key", "abbr"]
#     )

#     if not api_url or not token:
#         frappe.throw("API URL or API Key not configured")

#     url = f"{api_url.rstrip('/')}/v1/get-templates"

#     headers = {
#         "Authorization": f"Bearer {token}",
#         "Content-Type": "application/json"
#     }

#     response = requests.get(url, headers=headers, timeout=20)

#     if response.status_code != 200:
#         frappe.throw(response.text)

#     templates = response.json()

#     created, skipped = 0, 0

#     for tpl in templates:
#         template_name = tpl.get("name")

#         if frappe.db.exists(
#             "OnBBits Template",
#             {
#                 "template_name": template_name,
#                 "app_name": app
#             }
#         ):
#             skipped += 1
#             continue

#         body = tpl.get("body") or {}
#         footer = tpl.get("footer") or {}
#         header = tpl.get("header")

#         # FILTER
#         if header is not None and header.get("format") != "TEXT":
#             skipped += 1
#             continue

#         header_type = None
#         header_text = None

#         if header:
#             header_type = header.get("format")
#             if header_type == "TEXT":
#                 header_text = header.get("text")

#         # header_type = header.get("format")
#         # header_text = header.get("text") if header_type == "TEXT" else None

#         parameters = tpl.get("parameters", {})

#         header_parameter = None
#         header_params = parameters.get("header", [])

#         if header_params:
#             # Rule: Header can have ONLY ONE parameter
#             header_parameter = header_params[0].get("example")

#         doc = frappe.get_doc({
#             "doctype": "OnBBits Template",
#             "app_name": app,
#             "template_name": template_name,
#             "source": "OnBBits",
#             "category": tpl.get("category", ""),
#             "language": tpl.get("language", "en_US"),
#             "status": "Approved" if tpl.get("metaStatus") == "APPROVED" else "Pending",
#             "format": tpl.get("parameterFormat", "POSITIONAL"),
#             "template_type": header_type,
#             "header_text": header_text,
#             "header_parameter": header_parameter, 
#             "body_text": body.get("text"),
#             "footer_text": footer.get("text"),
#         })

#         # -----------------------------
#         # PARAMETERS (BODY)
#         # -----------------------------

#         # BODY parameters
#         parameters = tpl.get("parameters", {})
#         body_params = parameters.get("body", [])

#         if tpl.get("parameterFormat") == "NAMED":
#             for p in body_params:
#                 doc.append("template_parameters", {
#                     "parameter": p.get("name"),
#                     "value": p.get("example")
#                 })
#         else:
#             for idx, p in enumerate(body_params, start=1):
#                 doc.append("template_parameters", {
#                     "parameter": f"{{{{{idx}}}}}",
#                     "value": p.get("example")   # ✅ ALWAYS example
#                 })


#         # -----------------------------
#         # BUTTONS
#         # -----------------------------
#         for btn in tpl.get("buttons", []):
#             doc.append("template_buttons", {
#                 "button_type": btn.get("type"),
#                 "button_text": btn.get("text"),
#                 "url": btn.get("url"),
#                 "phone_number": btn.get("phone_number")
#             })

#         doc.insert(ignore_permissions=True)
#         doc.submit()

#         created += 1

#     frappe.db.commit()

#     return {
#         "total": len(templates),
#         "created": created,
#         "skipped": skipped
#     }

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

    response_data = response.json()

    if not response_data.get("success"):
        frappe.throw("Failed to fetch templates")

    templates = response_data.get("data", [])
  
    created = 0
    skipped = 0

    for tpl in templates:
        templateType  = tpl.get("templateType")
        template_name = tpl.get("name")

        if templateType != "STANDARD":
            skipped += 1
            continue

        if not template_name:
            skipped += 1
            continue

        if frappe.db.exists("OnBBits Template",{"template_name": template_name, "app_name": app}):
            skipped += 1
            continue

        body = tpl.get("body") or {}
        footer = tpl.get("footer") or {}
        header = tpl.get("header")

        # Only allow TEXT header or no header
        # if header is not None and header.get("format") != "TEXT":
        #     skipped += 1
        #     continue
        

        header_type = None
        header_text = None

        if header:
            header_type = header.get("format")
            if header_type == "TEXT":
                header_text = header.get("text")

        parameters = tpl.get("parameters") or {}

        # Header Parameter
        header_parameter = None
        header_params = parameters.get("header", [])

        if header_params:
            header_parameter = header_params[0].get("example")
        
        meta_status = tpl.get("metaStatus")

        if meta_status == "APPROVED":
            status = "Approved"
        elif meta_status == "REJECTED":
            status = "Rejected"
        else:
            status = "Pending"

        doc = frappe.get_doc({
            "doctype": "OnBBits Template",
            "app_name": app,
            "template_name": template_name,
            "source": "OnBBits",
            "category": tpl.get("category", ""),
            "language": tpl.get("language", "en_US"),
            "status": status,
            "format": tpl.get("parameterFormat", "POSITIONAL"),
            "template_type": header_type,
            "header_text": header_text,
            "header_parameter": header_parameter,
            "body_text": body.get("text"),
            "footer_text": footer.get("text"),
        })

        # ----------------------------------
        # BODY PARAMETERS
        # ----------------------------------
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
                    "value": p.get("example")
                })

        # ----------------------------------
        # BUTTONS
        # ----------------------------------
        for btn in tpl.get("buttons", []):
            doc.append("template_buttons", {
                "button_type": btn.get("type"),
                "button_text": btn.get("text"),
                "url": btn.get("url"),
                "phone_number": btn.get("phone_number")
            })

        try:
            doc.insert(ignore_permissions=True)
            doc.submit()
            created += 1

        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                f"Template Sync Failed - {template_name}"
            )
            skipped += 1

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

# def send_onbbits_template(doc, trigger_name): 
#     # -----------------------------
#     # Get Trigger
#     # -----------------------------
#     trigger = frappe.get_doc("OnBBits Template Trigger", trigger_name)

#     wa_setting = frappe.get_doc("OnBBits WA Setting", trigger.onbbits_app_name)

#     url = f"{wa_setting.api_url.rstrip('/')}/v1/send-template"

#     headers = {
#         "Content-Type": "application/json",
#         "token": wa_setting.api_key
#     }

#     # -----------------------------
#     # Receiver Number
#     # -----------------------------
#     number = doc.get(trigger.message_sent_to)
#     format_number = re.sub(r"\D", "", str(number))
#     if not number:
#         return

#     # -----------------------------
#     # Build Parameters
#     # -----------------------------
#     parameters = []
#     components = []

#     trigger_params = frappe.get_all(
#         "Template Trigger Parameter",
#         filters={"parent": trigger.name},
#         fields=["reference_field","static_value", "parameter"],
#         order_by="parameter asc"
#     )

#     for p in trigger_params:
#         value = p.static_value or doc.get(p.reference_field) or None
#         parameters.append({
#             "type": "text",
#             "text": str(value)
#         })

#     payload = {
#         "name": format_number,
#         "number": format_number,
#         "template_name": trigger.template_name,
#         "template_language": trigger.language or "en_US",
#         "components": [
#             {
#                 "type": "body",
#                 "parameters": parameters
#             }
#         ]
#     }

#     # -----------------------------
#     # Send API Request
#     # -----------------------------
#     response = requests.post(
#         url,
#         headers=headers,
#         data=json.dumps(payload)
#     )

#     frappe.log_error(
#         title="OnBBits Send Template",
#         message=response.text
#     )

#     if response.status_code not in (200, 201):
#         frappe.throw(response.text)

#     return response.json()

def get_media(trigger, doc):
    file_url = None
    file_name = None

    if trigger.media_source == "Static File":
        if not trigger.static_file:
            frappe.throw("Static File is not configured.")

        file_url = trigger.static_file
        file_name = trigger.static_file.split("/")[-1]

    elif trigger.media_source == "Document Field":
        if not trigger.document_field_name:
            frappe.throw("Document Field Name is not configured.")

        file_url = doc.get(trigger.document_field_name)

        if not file_url:
            frappe.throw(
                f"Field <b>{trigger.document_field_name}</b> is empty in "
                f"{doc.doctype} <b>{doc.name}</b>"
            )

        file_name = file_url.split("/")[-1]

    elif trigger.media_source == "Print Format PDF":
        pdf = frappe.get_print(
            doc.doctype,
            doc.name,
            print_format=trigger.print_format or "Standard",
            as_pdf=True
        )
        
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": f"{doc.name}.pdf",
            "content": pdf,
            "is_private": 0
        })
        file_doc.insert(ignore_permissions=True)

        file_url = file_doc.file_url
        frappe.log_error("PDF Generated", {file_url})
        file_name = file_doc.file_name

    # Convert relative URL to absolute URL
    if file_url:
        file_url = get_url(file_url)

    frappe.log_error(
        title="Media Debug",
        message=f"file_url={file_url}"
    )

    return file_url, file_name


def send_onbbits_template(doc, trigger_name):

    trigger = frappe.get_doc("OnBBits Template Trigger", trigger_name)

    wa_setting = frappe.get_doc(
        "OnBBits WA Setting",
        trigger.onbbits_app_name
    )

    url = f"{wa_setting.api_url.rstrip('/')}/v1/send-template"

    headers = {
        "Content-Type": "application/json",
        "token": wa_setting.api_key
    }

    # -----------------------------
    # Receiver Number
    # -----------------------------
    number = doc.get(trigger.message_sent_to)

    if not number:
        return

    format_number = re.sub(r"\D", "", str(number))

    # -----------------------------
    # Body Parameters
    # -----------------------------
    body_parameters = []

    trigger_params = frappe.get_all(
        "Template Trigger Parameter",
        filters={"parent": trigger.name},
        fields=[
            "reference_field",
            "static_value",
            "parameter"
        ],
        order_by="parameter asc"
    )

    for p in trigger_params:
        value = p.static_value or doc.get(p.reference_field) or ""

        body_parameters.append({
            "type": "text",
            "text": str(value)
        })

    # -----------------------------
    # Components
    # -----------------------------
    components = []

    # Header Media
    if trigger.template_type in ["IMAGE", "VIDEO", "DOCUMENT"]:

        file_url, file_name = get_media(trigger, doc)

        if trigger.template_type == "IMAGE":
            components.append({
                "type": "header",
                "parameters": [
                    {
                        "type": "image",
                        "image": {
                            "link": file_url
                        }
                    }
                ]
            })

        elif trigger.template_type == "VIDEO":
            components.append({
                "type": "header",
                "parameters": [
                    {
                        "type": "video",
                        "video": {
                            "link": file_url
                        }
                    }
                ]
            })

        elif trigger.template_type == "DOCUMENT":
            components.append({
                "type": "header",
                "parameters": [
                    {
                        "type": "document",
                        "document": {
                            "link": file_url,
                            "filename": file_name
                        }
                    }
                ]
            })

    # Body
    if body_parameters:
        components.append({
            "type": "body",
            "parameters": body_parameters
        })

    # -----------------------------
    # Payload
    # -----------------------------
    payload = {
        "name": format_number,
        "number": format_number,
        "template_name": trigger.template_name,
        "template_language": trigger.language or "en_US",
        "components": components
    }

    # -----------------------------
    # Send
    # -----------------------------
    response = requests.post(
        url,
        headers=headers,
        data=json.dumps(payload),
        timeout=30
    )

    frappe.log_error(
        title="OnBBits Send Template",
        message=json.dumps({
            "payload": payload,
            "response": response.text
        }, indent=2)
    )

    if response.status_code not in (200, 201):
        frappe.throw(response.text)

    return response.json()
