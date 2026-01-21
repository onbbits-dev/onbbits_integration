frappe.listview_settings['OnBBits Template'] = {
    onload(listview) {
        listview.page.add_inner_button('Sync Template', () => {
            sync_templates()
        });
        listview.page.add_inner_button(__('Sync Status'), () => {
            frappe.call({
                method: 'onbbits_integration.onbbits_api.sync_template_status',
                freeze: true,
                freeze_message: __('Syncing template status...'),
                callback: function (r) {
                    if (!r.message) return;
                    frappe.msgprint('Template Status Sync Completed')
                },
                error: function () {
                    frappe.msgprint({
                        title: __('Sync Failed'),
                        indicator: 'red',
                        message: __('Unable to sync template status. Please try again.')
                    });
                }
            });
        });
        
    }
};

function sync_templates() {
    const dialog = new frappe.ui.Dialog({
        title: 'Sync Templates',
        fields: [
            {
                fieldname: 'app',
                label: 'Select App',
                fieldtype: 'Link',
                options: 'OnBBits WA Setting',
                reqd: 1
            }
        ],
        primary_action_label: 'Sync',
        primary_action(values) {
            dialog.hide();

            frappe.call({
                method: 'onbbits_integration.onbbits_api.sync_templates',
                args: {
                    app: values.app
                },
                freeze: true,
                freeze_message: 'Syncing templates...',
                callback: function (r) {
                    if (r.message) {
                        const msg = r.message;
                
                        frappe.msgprint({
                            title: __('Template Sync Completed'),
                            indicator: msg.created > 0 ? 'green' : 'orange',
                            message: `
                                <b>Total Templates:</b> ${msg.total}<br>
                                <b>Created:</b> ${msg.created}<br>
                                <b>Skipped:</b> ${msg.skipped}
                            `
                        });
                    }
                }
            });
        }
    });

    dialog.show();
}
