# EmailJS Setup Guide for An Đô Website

## Step 1: Create EmailJS Account
1. Go to https://www.emailjs.com/
2. Sign up for a free account
3. Verify your email address

## Step 2: Create Email Service
1. Go to Email Services in your EmailJS dashboard
2. Click "Add New Service"
3. Choose Gmail (or your preferred email provider)
4. Connect your Gmail account (doanak000@gmail.com)
5. Note down the Service ID (e.g., "service_xyz123")

## Step 3: Create Email Template
1. Go to Email Templates in your dashboard
2. Click "Create New Template"
3. Use this template content:

**Template Name:** quote_request_template

**Subject:** New Quote Request from {{from_name}}

**Content:**
```
New quote request received from An Đô website:

From: {{from_name}}
Email: {{from_email}}
Subject: {{subject}}

Message:
{{message}}

---
This email was sent from the An Đô website quote request form.
```

4. Note down the Template ID (e.g., "template_abc456")

## Step 4: Get Public Key
1. Go to Account > General
2. Copy your Public Key (e.g., "user_def789")

## Step 5: Update Website Code
Replace these placeholders in ALL files that use EmailJS:

### Files to Update:
1. **contact.html** - Contact form
2. **reservation.html** - Quote request page
3. **index.html** - Quote form on homepage

### Replace These Placeholders:
- `YOUR_PUBLIC_KEY` with your actual public key
- `YOUR_SERVICE_ID` with your service ID
- `YOUR_TEMPLATE_ID` with your template ID

### Example Configuration:
```javascript
emailjs.init("user_def789"); // Your public key
emailjs.send('service_xyz123', 'template_abc456', templateParams) // Your service and template IDs
```

### Specific Locations to Update:

#### In contact.html (around line 245):
```javascript
emailjs.init("YOUR_PUBLIC_KEY"); // Replace with your key
emailjs.send('YOUR_SERVICE_ID', 'YOUR_TEMPLATE_ID', templateParams)
```

#### In reservation.html (around line 235):
```javascript
emailjs.init("YOUR_PUBLIC_KEY"); // Replace with your key
emailjs.send('YOUR_SERVICE_ID', 'YOUR_TEMPLATE_ID', templateParams)
```

#### In index.html (around line 580):
```javascript
emailjs.init("YOUR_PUBLIC_KEY"); // Replace with your key
emailjs.send('YOUR_SERVICE_ID', 'YOUR_TEMPLATE_ID', templateParams)
```

## Step 6: Testing
Test all 3 forms:
1. **Contact form** (contact.html) - Fill out and submit
2. **Quote request page** (reservation.html) - Fill out and submit
3. **Homepage quote form** (index.html) - Fill out and submit
4. Check doanak000@gmail.com for emails from all forms
5. Check EmailJS dashboard for delivery status

## Free Plan Limits
- 200 emails per month
- EmailJS branding in emails
- Basic support

For higher volume, consider upgrading to a paid plan.
