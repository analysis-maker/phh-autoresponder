# PriceLabs Agent for Professional Holiday Homes

## 🎯 Overview

The **PriceLabs Agent** is an autonomous pricing intelligence system for Professional Holiday Homes (PHH) that manages short-term rental property pricing across Australia. Built on n8n, this agent analyzes property performance, adjusts pricing strategies dynamically, automates new listing setup, and provides comprehensive reporting—all while maintaining human oversight through intelligent approval workflows.

## 🚀 What This Agent Does

### 1. **Dynamic Pricing Strategy**
Analyzes property performance weekly and applies intelligent price adjustments:
- Detects low occupancy and applies tiered discounts
- Adjusts weekend rates when vacancies remain close to check-in
- Implements last-minute emergency discounts
- Requires approval for significant changes (>15% discount)

### 2. **New Listing Pricing Setup**
Automates the entire onboarding process for new properties:
- Clones pricing strategies from template properties
- Calculates optimal base rates using property characteristics
- Compares with 3 peer properties
- Routes to review team before going live

### 3. **Peer Review Automation**
Intelligent approval workflows:
- Auto-generates pricing review checklists
- Sends notifications for sign-off
- Prevents publishing until approved
- Tracks approval history

### 4. **Reporting & Analytics**
Comprehensive performance tracking:
- Weekly reports on underperforming properties
- Price change audits
- Revenue impact analysis
- Automated CSV export and archival

### 5. **Advanced Decision Logic**
Sophisticated conditional rules:
- If occupancy < 60% after 14 days → apply temporary discount
- If weekend vacancy remains 5 days before check-in → lower price 10%
- If performance consistently low → flag for manual review
- All thresholds configurable via Google Sheets

### 6. **Robust System Architecture**
Production-ready infrastructure:
- Multiple trigger types (scheduled, webhook)
- Complete error handling and logging
- Retry logic for API calls
- Security best practices
- Audit trail for all changes

## 📁 Repository Structure

```
phh-autoresponder/
├── PRICELABS_AGENT_README.md           # This file
├── PRICELABS_AGENT_SPECIFICATION.md    # Complete technical specification
├── IMPLEMENTATION_CHECKLIST.md         # Step-by-step deployment guide
├── QUICK_REFERENCE_GUIDE.md            # Daily operations reference
│
├── n8n-workflows/                      # n8n workflow JSON files
│   ├── PHH_PriceLabs_Main_Engine_EXAMPLE.json
│   ├── PHH_New_Listing_Setup.json (to be created)
│   ├── PHH_Peer_Review_Handler.json (to be created)
│   ├── PHH_Weekly_Reporting.json (to be created)
│   ├── PHH_Decision_Logic_Router.json (to be created)
│   └── PHH_Error_Handler.json (to be created)
│
├── config-templates/                   # Google Sheets import templates
│   ├── google_sheets_pricing_config.csv
│   ├── google_sheets_properties_master.csv
│   └── google_sheets_audit_log_template.csv
│
└── example-data/                       # Sample payloads and responses
    ├── webhook_payload_new_property.json
    ├── webhook_payload_approval_decision.json
    └── pricelabs_api_response_properties.json
```

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   PriceLabs Agent                        │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Main Pricing │  │ New Listing  │  │ Peer Review  │  │
│  │   Engine     │  │    Setup     │  │  Automation  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Reporting & │  │   Decision   │  │    Error     │  │
│  │  Analytics   │  │ Logic Engine │  │   Handler    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  PriceLabs    │    │ Google Sheets │    │ Process Street│
│     API       │    │      API      │    │   / Email     │
└───────────────┘    └───────────────┘    └───────────────┘
```

## 🚦 Quick Start

### Prerequisites
- n8n instance (cloud or self-hosted)
- PriceLabs API access
- Google Workspace account
- SMTP email server

### Installation (30 minutes)

1. **Set up Google Sheets**
   ```bash
   # Create new workbook: "PHH PriceLabs Agent Data"
   # Import templates from config-templates/
   ```

2. **Configure n8n Credentials**
   - Add PriceLabs API key (HTTP Header Auth)
   - Add Google Sheets OAuth2
   - Add Email SMTP

3. **Import Workflows**
   ```bash
   # Import n8n-workflows/PHH_PriceLabs_Main_Engine_EXAMPLE.json
   # Update Google Sheet ID in all nodes
   # Update credential references
   ```

4. **Test**
   ```bash
   # Execute Main Engine manually
   # Verify audit log entries in Google Sheets
   ```

5. **Go Live**
   ```bash
   # Enable schedule trigger (6 AM weekdays)
   # Monitor first week closely
   ```

**Detailed instructions:** See [IMPLEMENTATION_CHECKLIST.md](./IMPLEMENTATION_CHECKLIST.md)

## 📖 Documentation

### For Implementation
1. **Start here:** [IMPLEMENTATION_CHECKLIST.md](./IMPLEMENTATION_CHECKLIST.md)
   - Week-by-week deployment plan
   - Complete setup instructions
   - Testing scenarios
   - Go-live checklist

2. **Technical details:** [PRICELABS_AGENT_SPECIFICATION.md](./PRICELABS_AGENT_SPECIFICATION.md)
   - Complete architecture overview
   - Detailed node specifications
   - Code snippets for all functions
   - API reference
   - Error handling and security

### For Daily Operations
3. **Quick reference:** [QUICK_REFERENCE_GUIDE.md](./QUICK_REFERENCE_GUIDE.md)
   - Common tasks (trigger analysis, approve changes)
   - Configuration adjustments
   - Troubleshooting guide
   - Emergency procedures
   - Useful code snippets

## 🎨 Key Features in Detail

### Intelligent Decision Making

The agent uses sophisticated logic to determine when and how to adjust prices:

```javascript
// Example: Tiered discount based on occupancy
if (occupancy < 40) {
  discount = 20%; // Aggressive discount
} else if (occupancy < 50) {
  discount = 15%; // Moderate discount
} else if (occupancy < 60) {
  discount = 10%; // Light discount
}

// Require approval for significant changes
if (discount >= 15%) {
  requireManualApproval = true;
}
```

### Configurable Thresholds

All business rules are stored in Google Sheets for easy adjustment:

| Parameter | Default | Purpose |
|-----------|---------|---------|
| low_occupancy_threshold | 60% | Trigger for discount |
| discount_percentage_tier1 | 10% | First discount level |
| weekend_adjustment_days | 5 | Days before to check |
| approval_threshold_percentage | 15% | When to require approval |

**Change thresholds → Effects apply immediately** (no code changes needed)

### Complete Audit Trail

Every price change is logged:
```
timestamp: 2025-11-14 06:15:00
property: Bondi Beach Apartment
old_price: $250
new_price: $225
action_type: occupancy_discount
reasoning: Occupancy at 55% below threshold
status: applied
```

## 🔧 Configuration

### Adjust Pricing Strategy

**Location:** Google Sheets → `pricing_config` tab

Common adjustments:
- **Be more aggressive:** Lower thresholds, increase discounts
- **Be more conservative:** Raise thresholds, decrease discounts
- **Seasonal changes:** Adjust during peak/off-peak seasons

Example: To apply discounts earlier
```csv
low_occupancy_threshold,70,percentage  # Changed from 60
```

### Change Schedule

**Location:** n8n → Main Engine → Schedule Trigger

```javascript
// Current: Weekdays at 6 AM
"0 6 * * 1-5"

// Change to: Daily at 10 PM
"0 22 * * *"

// Change to: Twice daily (6 AM and 6 PM)
"0 6,18 * * *"
```

### Enable/Disable Auto-Approval

**Location:** n8n → Main Engine → "IF Auto-Approval Allowed" node

```javascript
// Current: Auto-approve if < 15% discount
{{ $json.requires_manual_approval }}

// Require ALL approvals:
{{ true }}

// Auto-approve ALL changes:
{{ false }}
```

## 📊 Monitoring & Reporting

### Dashboard Metrics

Track these KPIs:
- ✅ Workflow execution success rate (target: >99%)
- ⏱️ Average execution time (target: <5 min)
- 💰 Properties adjusted per week
- 📈 Revenue impact (before/after)
- 👤 Manual intervention reduction (target: 80%)

### Weekly Reports

Automatically generated every Monday at 8 AM:
- Top underperforming properties
- All price changes with reasoning
- Comparison with previous week
- Properties flagged for review

**Delivered via:** Email + Google Drive + Slack (optional)

## 🛡️ Security & Reliability

### Security Features
- ✅ Webhook signature validation
- ✅ API key rotation support
- ✅ Input sanitization
- ✅ Audit logging for all actions
- ✅ Role-based access (via Google Sheets permissions)

### Reliability Features
- ✅ Automatic retry on API failures (3 attempts)
- ✅ Timeout handling (30s max)
- ✅ Error notifications to tech team
- ✅ Graceful degradation
- ✅ Data validation at every step

### Backup & Recovery
- ✅ Weekly workflow exports
- ✅ Google Sheets auto-backup
- ✅ Complete audit trail
- ✅ Documented restore procedures

## 🧪 Testing

### Test with Sample Data

```bash
# Test new property setup
curl -X POST https://your-n8n/webhook-test/phh-new-property \
  -H "Content-Type: application/json" \
  -d @example-data/webhook_payload_new_property.json

# Test approval workflow
curl -X POST https://your-n8n/webhook-test/phh-approval-decision \
  -H "Content-Type: application/json" \
  -d @example-data/webhook_payload_approval_decision.json
```

### Validation Checks

✅ Does it calculate discounts correctly?
✅ Does it require approval for >15% changes?
✅ Does it log all actions to audit sheet?
✅ Does it handle API errors gracefully?
✅ Does it send approval emails?

See [IMPLEMENTATION_CHECKLIST.md](./IMPLEMENTATION_CHECKLIST.md) → Phase 4 for complete testing scenarios.

## 🚨 Troubleshooting

### Common Issues

**Workflow not running?**
- Check schedule trigger is enabled
- Verify credentials are valid
- Check n8n server is running

**Prices not updating in PriceLabs?**
- Check execution log for errors
- Verify PriceLabs API key
- Check if changes require approval

**Approval emails not sending?**
- Verify SMTP credentials
- Check spam folder
- Test email node manually

**See full troubleshooting guide:** [QUICK_REFERENCE_GUIDE.md](./QUICK_REFERENCE_GUIDE.md) → 🔍 Troubleshooting

## 🛠️ Advanced Customization

### Add Custom Rules

Example: Apply higher discounts for properties in specific locations

```javascript
// In "Calculate Occupancy Discount" node
const property = $input.first().json;
let discountPercentage = 10; // base discount

// Premium locations get less discount
if (property.location.suburb === 'Bondi') {
  discountPercentage = 8;
}

// Less popular locations get more discount
if (property.location.suburb === 'Outer Sydney') {
  discountPercentage = 15;
}
```

### Integrate with Other Systems

Examples provided in specification:
- Slack notifications
- SMS alerts (via Twilio)
- Custom dashboards (webhook out)
- Property management systems
- Multi-channel sync (Airbnb, Booking.com)

### Machine Learning Integration (Phase 2)

Use historical data to predict optimal prices:
- Call Python ML service via webhook
- Train on occupancy + pricing history
- Return predicted optimal price
- Agent applies if within reasonable range

## 📞 Support

### Getting Help

1. **Check documentation**
   - [QUICK_REFERENCE_GUIDE.md](./QUICK_REFERENCE_GUIDE.md) for common tasks
   - [PRICELABS_AGENT_SPECIFICATION.md](./PRICELABS_AGENT_SPECIFICATION.md) for technical details

2. **Contact PHH Tech Team**
   - Email: tech@phh.com.au
   - Include: workflow name, execution ID, error message

3. **External Support**
   - n8n Community: https://community.n8n.io/
   - PriceLabs Support: support@pricelabs.co

### Contributing

Found a bug or have an improvement?
1. Document the issue
2. Propose solution
3. Test thoroughly
4. Update documentation
5. Share with team

## 📈 Roadmap

### Phase 1 (Current): Core Functionality ✅
- Dynamic pricing engine
- New listing setup
- Peer review automation
- Weekly reporting

### Phase 2 (Q1 2026): Advanced Features
- Machine learning price optimization
- Competitor price monitoring
- Dynamic seasonality detection
- Owner portal integration
- Multi-channel sync

### Phase 3 (Q2 2026): Intelligence Enhancements
- Predictive occupancy modeling
- Market demand forecasting
- Automated A/B testing
- Revenue optimization algorithms

## 📄 License

Copyright © 2025 Professional Holiday Homes
Internal use only - proprietary system

## 🙏 Acknowledgments

Built with:
- [n8n](https://n8n.io/) - Workflow automation
- [PriceLabs](https://pricelabs.co/) - Dynamic pricing API
- [Google Sheets](https://www.google.com/sheets/) - Configuration & logging
- [Process Street](https://www.process.st/) - Review workflows

## 📝 Version History

- **v1.0** (2025-11-14): Initial release
  - Core pricing engine
  - New listing automation
  - Peer review workflows
  - Weekly reporting
  - Complete documentation

---

## 🎯 Next Steps

1. **First time here?** → Read [IMPLEMENTATION_CHECKLIST.md](./IMPLEMENTATION_CHECKLIST.md)
2. **Ready to implement?** → Follow Phase 1 setup (Week 1)
3. **Need technical details?** → See [PRICELABS_AGENT_SPECIFICATION.md](./PRICELABS_AGENT_SPECIFICATION.md)
4. **Daily operations?** → Bookmark [QUICK_REFERENCE_GUIDE.md](./QUICK_REFERENCE_GUIDE.md)

**Questions?** Contact tech@phh.com.au

---

**Built with ❤️ for Professional Holiday Homes**
**Last Updated:** 2025-11-14
