// Copyright (c) 2025, It provides complete, centralized control over WhatsApp communication inside Frappe, enabling businesses to automate customer messaging with accuracy, reliability, and real-time synchronization. and contributors
// For license information, please see license.txt

frappe.ui.form.on("OnBBits WA Setting", {
    refresh(frm) {
        if (!frm.doc.api_key) {
            frm.set_intro(__(
                `<b>Let’s Get You Connected</b><br>
                Don’t have an account yet?
                <a href="https://app.onbbits.io/register" target="_blank">
                    Register here
                </a> to get started.`
            ));
        } else {
            frm.set_intro("");
        }
    },
});

