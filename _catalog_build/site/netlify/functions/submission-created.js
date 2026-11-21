'use strict';

// Netlify runs a function with this exact name automatically after every Netlify Forms
// submission. It passes the enquiry to the Nalanda WhatsApp hub so the customer gets a reply
// quickly and the team hears about it. The form itself, the stored submission and any email
// notification are unchanged, and this function can never block or break the form.
//
// Needs two environment variables in Netlify (Site settings > Environment variables):
//   HUB_LEADS_URL     https://srv1693296.hstgr.cloud/lead/website
//   HUB_LEADS_SECRET  the shared secret (same value as LEADS_SECRET on the hub)

const crypto = require('node:crypto');

const FORM_NAME = 'corporate-gifting-enquiry';

exports.handler = async (event) => {
  try {
    const body = JSON.parse(event.body || '{}');
    const payload = body.payload || {};
    if (payload.form_name !== FORM_NAME) return { statusCode: 200, body: 'ignored' };

    const d = payload.data || {};
    if (d['bot-field']) return { statusCode: 200, body: 'spam' }; // honeypot was filled in

    const url = process.env.HUB_LEADS_URL;
    const secret = process.env.HUB_LEADS_SECRET;
    if (!url || !secret) {
      console.error('WhatsApp hub is not configured (HUB_LEADS_URL, HUB_LEADS_SECRET)');
      return { statusCode: 200, body: 'not configured' };
    }

    const lead = JSON.stringify({
      name: d.name,
      company: d.company,
      phone: d.phone,
      email: d.email,
      occasion: d.occasion,
      quantity: d.quantity,
      budget: d.budget,
      message: d.message,
      source: 'corporategiftingindia.co',
    });
    const signature = 'sha256=' + crypto.createHmac('sha256', secret).update(lead).digest('hex');

    const res = await fetch(url, {
      method: 'POST',
      headers: { 'content-type': 'application/json', 'x-lead-signature': signature },
      body: lead,
      signal: AbortSignal.timeout(8000),
    });
    console.log('WhatsApp hub answered', res.status); // never log the customer's details
  } catch (e) {
    console.error('WhatsApp lead bridge failed:', e.message);
  }
  return { statusCode: 200, body: 'ok' };
};
