# PriceLabs Agent Quick Reference Guide

## 📋 Essential Information At-A-Glance

### Workflow URLs

```
Main Engine (Manual Trigger):
https://[your-n8n]/webhook-test/phh-pricing-trigger

New Property Webhook:
https://[your-n8n]/webhook/phh-new-property

Approval Decision Webhook:
https://[your-n8n]/webhook/phh-approval-decision

Error Handler:
https://[your-n8n]/webhook/phh-error-handler
```

### Google Sheet ID
```
Sheet ID: [YOUR_SHEET_ID_HERE]
URL: https://docs.google.com/spreadsheets/d/[YOUR_SHEET_ID_HERE]
```

### Key Contacts
- Pricing Team: pricing-team@phh.com.au
- Tech Support: tech@phh.com.au
- PriceLabs Support: support@pricelabs.co

---

## 🚀 Common Tasks

### Manually Trigger Pricing Analysis
1. Go to n8n dashboard
2. Find workflow: "PHH PriceLabs Main Engine"
3. Click "Execute Workflow"
4. Check execution log for results

### Add a New Property
```bash
curl -X POST https://[your-n8n]/webhook/phh-new-property \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Signature: [signature]" \
  -d @example-data/webhook_payload_new_property.json
```

### Approve a Pending Price Change
1. Check email for approval request
2. Review property details and proposed price
3. Click approval link (if automated)
4. OR send webhook:
```bash
curl -X POST https://[your-n8n]/webhook/phh-approval-decision \
  -H "Content-Type: application/json" \
  -d '{
    "decision": {
      "status": "approved",
      "reviewer_email": "your-email@phh.com.au",
      "notes": "Approved - looks good"
    },
    "property_data": {
      "property_id": "12345",
      "proposed_base_rate": 225
    }
  }'
```

### Check Recent Price Changes
1. Open Google Sheet: "PHH PriceLabs Agent Data"
2. Go to tab: "pricing_audit_log"
3. Sort by timestamp (newest first)
4. Review status column for pending/applied

### View Weekly Report
1. Check email Monday mornings (~8:15 AM)
2. Download attached CSV
3. OR check Google Drive folder: "Pricing Reports"
4. OR check Google Sheet tab: "reports_archive"

---

## ⚙️ Configuration Adjustment Guide

### Change Discount Thresholds

**Location:** Google Sheets → `pricing_config` tab

Common adjustments:

| Parameter | Current | To Increase Discounts | To Decrease Discounts |
|-----------|---------|----------------------|----------------------|
| low_occupancy_threshold | 60 | Increase to 70 | Decrease to 50 |
| discount_percentage_tier1 | 10 | Increase to 12-15 | Decrease to 5-8 |
| weekend_adjustment_days | 5 | Increase to 7 | Decrease to 3 |

**After changes:** Wait for next scheduled run OR trigger manually

### Change Schedule Timing

**Location:** n8n → PHH PriceLabs Main Engine → Schedule Trigger node

Current: `0 6 * * 1-5` (6 AM weekdays)

Common alternatives:
- `0 22 * * *` - 10 PM every day
- `0 8 * * 1` - 8 AM Mondays only
- `0 6,18 * * *` - 6 AM and 6 PM daily

### Enable/Disable Auto-Approval

**Location:** n8n → PHH PriceLabs Main Engine → "IF Auto-Approval Allowed" node

Change condition:
```javascript
// Current: Auto-approve if discount < 15%
{{ $json.requires_manual_approval }}

// To require all approvals:
{{ true }}

// To approve all changes:
{{ false }}
```

---

## 🔍 Troubleshooting

### Problem: Workflow Failed

**Check:**
1. n8n → Executions → Find failed execution
2. Click to view error details
3. Check error message

**Common Fixes:**

| Error Message | Solution |
|--------------|----------|
| "Timeout" | Increase timeout in HTTP Request node (Options → Timeout → 30000) |
| "Rate limit" | Add Wait node (2 seconds) between API calls |
| "Invalid credentials" | Re-authenticate in Credentials panel |
| "Sheet not found" | Verify Google Sheet ID in workflow |
| "Property not found" | Check property_id exists in PriceLabs |

### Problem: No Price Changes Applied

**Check:**
1. Google Sheets → `pricing_audit_log`
2. Look for recent entries with status "pending_approval"
3. Check if `action_needed` is false in execution data

**Possible Reasons:**
- All properties above occupancy threshold
- Recent price changes within last 6 hours
- Configuration values too strict

### Problem: Wrong Prices Applied

**Immediate Action:**
1. Pause workflow: n8n → Workflow → Active (toggle OFF)
2. Manually revert in PriceLabs
3. Log issue in system_logs sheet

**Investigation:**
1. Check execution data
2. Review calculation logic in "Calculate Performance Metrics" node
3. Verify config values in Google Sheets
4. Test with individual property

### Problem: Approval Emails Not Sending

**Check:**
1. n8n → Credentials → Email SMTP → Test
2. Check email server logs
3. Verify email addresses in workflow nodes

**Common Fixes:**
- Use App Password (not regular password) for Gmail
- Check spam folder
- Verify SMTP port (587 for TLS, 465 for SSL)

---

## 📊 Data Schema Quick Reference

### Property Object (from PriceLabs)
```javascript
{
  "id": "12345",
  "name": "Property Name",
  "base_price": 250,
  "occupancy_last_30_days": 55,
  "next_booking_date": "2025-11-20",
  "status": "active"
}
```

### Pricing Config Row
```javascript
{
  "parameter_name": "low_occupancy_threshold",
  "value": "60",
  "data_type": "percentage"
}
```

### Audit Log Entry
```javascript
{
  "timestamp": "2025-11-14 06:15:00",
  "property_id": "12345",
  "old_price": 250,
  "new_price": 225,
  "action_type": "occupancy_discount",
  "status": "applied"
}
```

---

## 🔐 Security Checklist

### Monthly Security Tasks
- [ ] Rotate PriceLabs API key
- [ ] Review n8n access logs
- [ ] Check webhook signature validation
- [ ] Review Google Sheets permissions
- [ ] Update email passwords

### Best Practices
- Never commit credentials to git
- Use environment variables for sensitive data
- Enable 2FA on all accounts
- Regularly backup workflows
- Monitor for unusual API activity

---

## 📈 Performance Benchmarks

### Expected Execution Times
- Main Engine (10 properties): ~30 seconds
- Main Engine (50 properties): ~2 minutes
- New Listing Setup: ~15 seconds
- Weekly Report: ~45 seconds

### API Call Limits
- PriceLabs: 1000 calls/day (check your plan)
- Google Sheets: 100 calls/100 seconds/user
- Process Street: 500 calls/hour

### Optimization Tips
1. Cache property data (refresh hourly vs every execution)
2. Batch Google Sheets writes (10 rows at once)
3. Use pagination for large property lists
4. Add delays between API calls (1-2 seconds)

---

## 🧪 Testing Commands

### Test PriceLabs Connection
```bash
curl -X GET "https://api.pricelabs.co/v1/properties" \
  -H "X-API-Key: YOUR_API_KEY"
```

### Test Google Sheets Access
```bash
# Use Google Sheets API Explorer:
https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/get

# Method: spreadsheets.values.get
# spreadsheetId: [YOUR_SHEET_ID]
# range: pricing_config!A1:G100
```

### Test Webhook Endpoint
```bash
# Test new property webhook
curl -X POST https://[your-n8n]/webhook-test/phh-new-property \
  -H "Content-Type: application/json" \
  -d '{"property_name":"Test Property","bedrooms":2}'

# Should return: {"status":"received"}
```

---

## 📝 Useful Code Snippets

### Get Config Value in Function Node
```javascript
const config = $('Load Pricing Config').all();
const configMap = {};
config.forEach(row => {
  configMap[row.json.parameter_name] = parseFloat(row.json.value);
});

const threshold = configMap.low_occupancy_threshold || 60;
```

### Format Price for Display
```javascript
const formatPrice = (price) => {
  return `$${Math.round(price).toLocaleString()}`;
};

// Usage: formatPrice(250.50) → "$251"
```

### Calculate Date Range
```javascript
const today = new Date();
const weekAgo = new Date();
weekAgo.setDate(today.getDate() - 7);

const dateRange = {
  start: weekAgo.toISOString().split('T')[0],
  end: today.toISOString().split('T')[0]
};
```

### Safe Property Access
```javascript
const occupancy = $json?.performance_metrics?.occupancy_last_30_days ?? 0;
const nextBooking = $json?.booking_data?.next_booking_date ?? null;
```

---

## 🆘 Emergency Procedures

### Complete System Failure

1. **Immediate Actions:**
   - Pause all n8n workflows
   - Send email to pricing team
   - Revert to manual pricing process

2. **Investigation:**
   - Check n8n server status
   - Check PriceLabs API status
   - Check Google Sheets access
   - Review recent changes

3. **Recovery:**
   - Fix identified issue
   - Test with single property
   - Gradually re-enable workflows
   - Monitor closely for 24 hours

### Incorrect Prices Applied to Many Properties

1. **Stop Further Changes:**
   - Pause Main Engine workflow immediately
   - Document affected property IDs

2. **Revert Prices:**
   - Export audit log from Google Sheets
   - Filter by timestamp of error
   - Manually revert in PriceLabs
   - OR use bulk API update script

3. **Root Cause Analysis:**
   - Review calculation logic
   - Check config values
   - Identify code bug
   - Document fix

4. **Prevention:**
   - Add validation checks
   - Implement price change limits
   - Add manual approval for >X% changes

### Data Breach or Security Incident

1. **Immediately:**
   - Disable all webhooks
   - Rotate all API keys
   - Change all passwords
   - Contact security team

2. **Assessment:**
   - Review access logs
   - Identify compromised accounts
   - Determine data exposure

3. **Recovery:**
   - Implement security patches
   - Re-enable with new credentials
   - Monitor for suspicious activity

---

## 📞 Support Escalation

### Level 1: Self-Service
- Check this guide
- Review error logs
- Search n8n community forum

### Level 2: Team Support
- Contact: tech@phh.com.au
- Provide: Workflow name, execution ID, error message
- Response time: 2 hours (business hours)

### Level 3: External Support
- PriceLabs: support@pricelabs.co
- n8n (if cloud): support@n8n.io
- Response time: 24 hours

---

## 📚 Additional Resources

- [Full Specification](./PRICELABS_AGENT_SPECIFICATION.md)
- [Implementation Checklist](./IMPLEMENTATION_CHECKLIST.md)
- [n8n Documentation](https://docs.n8n.io/)
- [PriceLabs API Docs](https://pricelabs.co/api-docs)
- [Google Sheets API](https://developers.google.com/sheets/api)

---

**Last Updated:** 2025-11-14
**Version:** 1.0
**Maintained By:** PHH Tech Team
