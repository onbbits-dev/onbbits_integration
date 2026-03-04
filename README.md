# OnBBits Integration

**OnBBits Integration** connects your Frappe / ERPNext system with the OnBBits WhatsApp Messaging Platform.
It enables automated WhatsApp messaging, template synchronization, and real-time communication directly from your ERP.

---

## Key Features

*  Seamless integration with OnBBits WhatsApp Platform
*  Template synchronization & status tracking
*  Automatic WhatsApp message triggers based on document events
*  Multi-app support
*  Secure API-based authentication

---

## Installation

Install using the Bench CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench --site your-site-name install-app onbbits_integration
```

---

## Initial Setup

To start using the app, you need your **API Key** from the OnBBits portal.

---

### Step 1: Get API Key from OnBBits

1. Log in to your OnBBits account.
2. Open your App.
3. Locate **API Key** in the side navigation.
4. Copy the API Key.

<img width="1560" height="1120" alt="API Key" src="https://github.com/user-attachments/assets/3cf3012a-3a03-4250-9371-a5a24ee5c496" />

---

### Step 2: Configure API Key in Frappe / ERPNext

1. Open your Frappe / ERPNext system.
2. Navigate to
   **OnBBits Integration → OnBBits WA Settings**
3. Paste the API Key.
4. Click **Save**.

<img width="1560" height="1120" alt="WA Settings" src="https://github.com/user-attachments/assets/f0885a17-feb8-4d48-927e-f997b33531ee" />

💡 You can manage multiple OnBBits apps from the same settings screen.

---

## Managing WhatsApp Templates

Templates are predefined WhatsApp messages approved by Meta.

---

### Step 1: View Templates

Navigate to:

**OnBBits Templates**

Here you can see:

* Template Name
* Language
* Category
* Template Type
* Status (Approved / Pending)

<img width="2023" height="1119" alt="Template List" src="https://github.com/user-attachments/assets/b2701ca9-6a75-4420-942b-bd74fb3024c7" />

---

### Step 2: Sync Templates

1. Click **Sync Templates**
2. Select the App
3. Templates will be fetched from OnBBits

<img width="2023" height="1119" alt="Sync Templates" src="https://github.com/user-attachments/assets/be3d0dea-6577-4968-b9cb-3dccedbc60e8" />

<img width="2023" height="1119" alt="Templates Synced" src="https://github.com/user-attachments/assets/a12b7f17-3a91-4dc1-9d86-f50f52b58478" />

Use this when:

* A new template is created
* Templates are updated
* Templates are missing in Frappe

---

### Step 3: Sync Template Status

Template status syncs automatically every 1 hour.

You can also sync manually:

1. Go to **WhatsApp Templates**
2. Click **Sync Status**

<img width="2023" height="1119" alt="Sync Status" src="https://github.com/user-attachments/assets/d3a8f110-98ff-4cf0-a292-c781db2ae751" />

---

## Automatic Message Triggers

Automatically send WhatsApp messages when documents are created, updated, submitted, or cancelled.

---

## Create a Trigger Rule

1. Go to **WhatsApp Template Trigger**
2. Click **New**
3. Select:

   * App Name
   * DocType (e.g., Lead, Sales Order)
   * Event (Insert, Submit, Update, Cancel)
4. Choose **Message Sent To**

   * Select a Phone field
   * If none exists, click **Auto Create “Message Sent To” Field**
5. Select WhatsApp Template
6. Map Template Parameters:

### Parameter Mapping Options

*  **Reference Field**
  Map values from the document
  (e.g., customer_name, city, state)

*  **Static Value**
  Send fixed values
  (e.g., "12:00 PM")

7. Click **Save**

<img width="2032" height="1117" alt="Trigger Setup" src="https://github.com/user-attachments/assets/35dd5e7b-3bd8-4dac-a997-67068055b7d4" />

Mapped fields fetch data dynamically from the document.
Static values remain constant for every message.

---

## Quick Start Summary

1. Get API Key from OnBBits
2. Add API Key in WA Settings
3. Sync Templates
4. Create Trigger Rules
5. Start sending WhatsApp messages automatically

---

## Security

* Secure API authentication
* No WhatsApp credentials stored locally
* Controlled template-based messaging

---

## License

MIT
