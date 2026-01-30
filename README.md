# Onbbits Integration

OnBBits Integration is an app that seamlessly connects your ERP system with the OnBBits WhatsApp Messaging Platform, enabling automated messaging, template management, and real-time WhatsApp communication directly from Frappe / ERPNext.

## Features

- Integration with the OnBBits WhatsApp Messaging Platform
- Template synchronization and status tracking
- Automatic WhatsApp message triggering based on document events
- Multi-app support
- Secure API-based authentication


## Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app onbbits_integration
```

## Quick Start

- Get your **API Key** from the OnBBits Portal.
- Go to **OnBBits Integration → OnBBits WA Setting** and add the API Key.
- Sync WhatsApp templates from **OnBBits Templates**.
- Create automatic message rules using **WhatsApp Template Trigger**.

## Documentation
Detailed setup instructions and screenshots are available here:
https://docs.google.com/document/d/1po81UGTuki9pyUNxS5IpUteXIsOC8EfymDvwdRK1c1g/edit?tab=t.0 

## License

mit
