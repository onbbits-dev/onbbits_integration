// Copyright (c) 2025, It provides complete, centralized control over WhatsApp communication inside Frappe, enabling businesses to automate customer messaging with accuracy, reliability, and real-time synchronization. and contributors
// For license information, please see license.txt

frappe.ui.form.on("OnBBits Template", {
	refresh(frm){
        frappe.after_ajax(() => {
            lock_fetched_rows(frm, "template_parameters");
        });
        update_preview(frm);
        if(frm.is_new()){
            frm.set_value("status", "Pending");
            frm.set_value("source", "Frappe");
        }
    },
    header_text(frm) {
        let text = frm.doc.header_text || "";

        // Match anything inside {{ }}
        let hasParam = /{{\s*[^}]+\s*}}/.test(text);

        // If contains {{1}} → show + make mandatory
        frm.set_df_property("header_parameter", "reqd", hasParam);
        frm.set_df_property("header_parameter", "hidden", !hasParam);
        if (!hasParam) {
            frm.set_value("header_parameter", "");
        }
    },
    template_name(frm) {
        validate_lowercase_field(frm)
    },
    body_text(frm) {
        add_placeholders(frm);
        if (frm.doc.body_text.length > 1024) {
            frappe.msgprint("Body Text cannot exceed 1024 characters.");
            frm.set_value("body_text", frm.doc.body_text.substring(0, 1024));
        }
        update_preview(frm);
    },
    before_save(frm) {
        add_placeholders(frm);
        validate_body_text(frm);
        if(frm.doc.category === "AUTHENTICATION"){
            frappe.throw("You cannot create templates under the 'Authentication' category.");
        }
    },
    template_parameters_on_form_rendered(frm, grid_row) {
        remove_delete_button(grid_row)
    },

});


function add_placeholders(frm) {
    let text = frm.doc.body_text || "";

    // Extract placeholders like {{1}}, {{abc}}, {{6}}
    let matches = [...text.matchAll(/{{\s*([^{}]+)\s*}}/g)];
    let placeholders = [...new Set(matches.map(m => m[0]))];

    // --- ADD missing placeholders ---
    placeholders.forEach(ph => {
        let exists = (frm.doc.template_parameters || [])
            .some(r => r.parameter === ph);

        if (!exists) {
            let row = frm.add_child("template_parameters");
            row.parameter = ph;
        }
    });

    // --- DELETE placeholders removed from body_text ---
    let rows = frm.doc.template_parameters || [];
    rows.forEach((row, i) => {
        if (!placeholders.includes(row.parameter)) {
            frm.get_field("template_parameters").grid.grid_rows[i].remove();
        }
    });

    frm.refresh_field("template_parameters");
}

function lock_fetched_rows(frm, child_table_name) {
    const grid = frm.fields_dict[child_table_name]?.grid;
    if (!grid) return;

     setTimeout(() => {
        // Prevent removing all rows or adding rows via toolbar
        grid.wrapper.find('.grid-remove-all-rows').hide();
        grid.wrapper.find('.grid-add-row').hide();
        grid.wrapper.find('.grid-remove-rows').hide();
    }, 300); // wait 300ms for grid render
}
function remove_delete_button(grid_row){
    var grid_row = cur_frm.open_grid_row();
    var child = grid_row.doc;
	     frappe.after_ajax(() => {
                const dialog = grid_row.grid_form?.wrapper;
                if (dialog) {
                    $(dialog).find('.grid-delete-row').hide();
                    $(dialog).find('.grid-insert-row-below').hide();
                    $(dialog).find('.grid-insert-row').hide();
                    $(dialog).find('.grid-duplicate-row').hide();

                }
    	})
}

function validate_body_text(frm) {
    let text = frm.doc.body_text || "";

    // 1️⃣ Check max length 1024
    if (text.length > 1024) {
        frappe.msgprint("Body Text cannot exceed 1024 characters.");
        frm.set_value("body_text", text.substring(0, 1024));
        return;
    }

    // 2️⃣ Check if starts or ends with {{...}}
    // Pattern: {{something}}
    const param_pattern = /^\{\{.*?\}\}$/;

    // Check start
    let starts_with_param = text.trim().match(/^(\{\{.*?\}\})/);

    // Check end
    let ends_with_param = text.trim().match(/(\{\{.*?\}\})$/);

    if (starts_with_param || ends_with_param) {
        frappe.msgprint("Placeholders (such as {{...}}) cannot be at the beginning or end of the Body Text. Please move them inside the content.");
        // remove parameter from start or end
        text = text.trim().replace(/^(\{\{.*?\}\})/, "");
        text = text.trim().replace(/(\{\{.*?\}\})$/, "");
        frm.set_value("body_text", text.trim());
        return;
    }
}

function validate_lowercase_field(frm) {
    let value = frm.doc.template_name || "";

    // Allowed: a–z, 0–9, _
    let pattern = /^[a-z0-9_]+$/;

    if (!pattern.test(value)) {
        frappe.msgprint(
            "Use lowercase letters, numbers, and underscores only."
        );

        // Auto-clean invalid characters
        value = value.toLowerCase().replace(/[^a-z0-9_]/g, "");
        frm.set_value("template_name", value);
    }
}

function build_preview(header, body, footer, header_params, body_params, buttons) {
    if (!body && !header && !footer) return "";

    let header_html = header || "";
    let body_html   = body || "";
    let footer_html = footer || "";

    // Replace HEADER parameters
    if (/{{\s*[^}]+\s*}}/.test(header_html)) {
        header_html = header_html.replace(
            /{{\s*[^}]+\s*}}/g,
            header_params || "<span style='opacity:0.6'>$&</span>"
        );
    }

    // Replace BODY parameters
    (body_params || []).forEach(row => {
        if (row.parameter) {
            body_html = body_html.replaceAll(row.parameter, row.value || "");
        }
    });

    // Formatting helper
    function format_text(text) {
        return text
            .replace(/\n/g, "<br>")
            .replace(/\*(.*?)\*/g, "<b>$1</b>")
            .replace(/_(.*?)_/g, "<i>$1</i>")
            .replace(/~(.*?)~/g, "<s>$1</s>");
    }

    header_html = format_text(header_html);
    body_html   = format_text(body_html);
    footer_html = format_text(footer_html);

    // Buttons
    let button_html = "";
    buttons.forEach(btn => {
        if (btn.button_text) {
            button_html += `
                <div class="preview-button">
                ${btn.button_type === "URL" ? `
                    <svg class="wa-btn-icon"
                        xmlns='http://www.w3.org/2000/svg'
                        viewBox='0 0 128 128'>
                        <path d='M 84 11 C 82.3 11 81 12.3 81 14 C 81 15.7 82.3 17 84 17 L 106.80078 17 L 60.400391 63.400391 C 59.200391 64.600391 59.200391 66.499609 60.400391 67.599609 C 61.000391 68.199609 61.8 68.5 62.5 68.5 C 63.2 68.5 63.999609 68.199609 64.599609 67.599609 L 111 21.199219 L 111 44 C 111 45.7 112.3 47 114 47 C 115.7 47 117 45.7 117 44 L 117 14 C 117 12.3 115.7 11 114 11 L 84 11 z M 24 31 C 16.8 31 11 36.8 11 44 L 11 104 C 11 111.2 16.8 117 24 117 L 84 117 C 91.2 117 97 111.2 97 104 L 97 59 C 97 57.3 95.7 56 94 56 C 92.3 56 91 57.3 91 59 L 91 104 C 91 107.9 87.9 111 84 111 L 24 111 C 20.1 111 17 107.9 17 104 L 17 44 C 17 40.1 20.1 37 24 37 L 69 37 C 70.7 37 72 35.7 72 34 C 72 32.3 70.7 31 69 31 L 24 31 z'/>
                    </svg>
                ` : ""}
                    ${btn.button_type === "PHONE_NUMBER" ? "📞" : ""}
                    ${btn.button_text}
                </div>
            `;
        }
    });

    // return `
    //     <div class="preview-box">
    //         ${header_html ? `<div class="preview-header">${header_html}</div>` : ""}
    //         ${body_html ? `<div class="preview-text">${body_html}</div>` : ""}
    //         ${button_html}
    //         ${footer_html ? `<hr><div class="preview-footer">${footer_html}</div>` : ""}
    //     </div>

    //     <div class="preview-disclaimer">
    //         Disclaimer: This is a visual preview only. Final rendering may differ on WhatsApp.
    //     </div>
    // `;
    return `
    <div class="preview-box">
        <div class="preview-top-bar"></div>
        <div class="preview-content">
            ${header_html ? `<div class="preview-header">${header_html}</div>` : ""}
            ${body_html ? `<div class="preview-text">${body_html}</div>` : ""}
            ${button_html}
            ${footer_html ? `<div class="preview-footer">${footer_html}</div>` : ""}
        </div>
    </div>

    `;

}

function update_preview(frm) {

    let header_params = frm.doc.header_parameter || "";
    let body_params   = frm.doc.template_parameters || [];

    let preview_html = build_preview(
        frm.doc.header_text,
        frm.doc.body_text,
        frm.doc.footer_text,
        header_params,
        body_params,
        frm.doc.template_buttons || []
    );

    // frm.fields_dict.body_preview.$wrapper.html(`
    //     <style>

    //         .preview-box {
    //             max-width: 380px;
    //             background: #fff;
    //             border-radius: 14px;
    //             padding: 18px;
    //             box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    //             font-family: system-ui, sans-serif;
    //             border-left: 5px solid #25D366;
    //         }

    //         .preview-header {
    //             font-size: 15px;
    //             font-weight: 600;
    //             margin-bottom: 10px;
    //             color: #111;
    //         }

    //         .preview-text {
    //             font-size: 14px;
    //             line-height: 20px;
    //             color: #444;
    //         }

    //         .preview-footer {
    //             font-size: 12px;
    //             color: #777;
    //             margin-top: 12px;
    //         }

    //         .preview-button {
    //             width: 100%;
    //             border: 1.5px solid #25D366;
    //             border-radius: 8px;
    //             padding: 10px 14px;
    //             margin-top: 10px;
    //             font-size: 14px;
    //             text-align: center;
    //             cursor: pointer;
    //             color: #25D366;
    //             font-weight: 600;
    //             background: #fff;
    //         }

    //         .preview-button i {
    //             margin-right: 6px;
    //         }

    //        .preview-container {
    //             display: flex;
    //             flex-direction: column;
    //             align-items: center;
    //             padding: 20px 0;
    //             width: 100%;
    //         }

    //         .preview-disclaimer {
    //             margin-top: 8px;
    //             font-size: 11px;
    //             color: #888;
    //             text-align: center;
    //             max-width: 380px;
    //         }
    //     </style>

    //     <div class="preview-container">
    //         ${preview_html}
    //     </div>
    // `);
    frm.fields_dict.body_preview.$wrapper.html(`
        <style>
        .preview-outer {
            background: #f4efe9;
            padding: 20px;
            border-radius: 12px;
            display: flex;
            justify-content: center;
        }
        
        .preview-box {
            max-width: 380px;
            width: 100%;
            background: #fff;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 4px 14px rgba(0,0,0,0.1);
            font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        .preview-top-bar {
            height: 8px;
            background: #0b6f57;
        }
        .wa-btn-icon {
            width: 16px;
            height: 16px;
            color: #25D366 !important;   /* WhatsApp green */
            flex-shrink: 0;
        }
        .wa-btn-icon path {
            stroke: currentColor;
            stroke-width: 1.4;
        }
        
        .preview-image {
            height: 120px;
            background: #f2f2f2;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .image-icon {
            width: 40px;
            height: 40px;
            border: 2px solid #bdbdbd;
            border-radius: 6px;
            position: relative;
        }

        .image-icon::before {
            content: "";
            position: absolute;
            bottom: 6px;
            left: 6px;
            width: 16px;
            height: 10px;
            background: #bdbdbd;
            clip-path: polygon(0 100%, 40% 40%, 65% 70%, 100% 20%, 100% 100%);
        }

        .image-icon::after {
            content: "";
            position: absolute;
            top: 6px;
            right: 6px;
            width: 6px;
            height: 6px;
            background: #bdbdbd;
            border-radius: 50%;
        }
        
        .preview-content {
            padding: 16px;
        }
        
        .preview-header {
            font-size: 15px;
            font-weight: 600;
            color: #111;
            margin-bottom: 10px;
        }
        
        .preview-text {
            font-size: 14px;
            line-height: 1.45;
            color: #444;
        }
        
        .preview-text p {
            margin: 0 0 8px;
        }
        
        .preview-button {
            border: 1.5px solid #25D366;
            border-radius: 8px;
            padding: 10px;
            margin-top: 14px;
            text-align: center;
            font-size: 14px;
            font-weight: 600;
            color: #25D366;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }
        
        .preview-footer {
            font-size: 12px;
            color: #777;
            margin-top: 12px;
        }
        
        .preview-disclaimer {
            font-size: 11px;
            color: #888;
            margin-top: 8px;
            text-align: center;
        }
        </style>
        
        <div class="preview-outer">
            ${preview_html}
        </div>
        `);
        
}
