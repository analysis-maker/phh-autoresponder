# PriceLabs Agent Implementation Checklist

## Phase 1: Environment Setup (Week 1)

### n8n Installation
- [ ] Install n8n (cloud or self-hosted)
- [ ] Set up SSL certificate for production
- [ ] Configure environment variables
- [ ] Set up backup strategy for workflows
- [ ] Configure timezone to AEST (Australia/Sydney)

### Credentials Configuration
- [ ] Add PriceLabs API credentials
  - Credential type: HTTP Header Auth
  - Header name: `X-API-Key`
  - API Key value: `[Get from PriceLabs dashboard]`
- [ ] Add Google Sheets OAuth2
  - Create service account in Google Cloud Console
  - Enable Google Sheets API
  - Download credentials JSON
  - Add to n8n credentials
- [ ] Add Email SMTP credentials
  - Server: smtp.gmail.com (or your provider)
  - Port: 587
  - Username: pricing-agent@phh.com.au
  - Password/App Password: [Secure password]
- [ ] Add Process Street API credentials (optional)
  - Get API key from Process Street settings
  - Add as HTTP Header Auth

### Google Sheets Setup
- [ ] Create new Google Sheets workbook: "PHH PriceLabs Agent Data"
- [ ] Create sheet: `pricing_config`
  - Import from: `/config-templates/google_sheets_pricing_config.csv`
- [ ] Create sheet: `properties_master`
  - Import from: `/config-templates/google_sheets_properties_master.csv`
- [ ] Create sheet: `pricing_audit_log`
  - Headers: timestamp, property_id, property_name, old_price, new_price, change_amount, action_type, reasoning, requires_approval, status
- [ ] Create sheet: `system_logs`
  - Headers: timestamp, workflow, execution_id, log_level, message, data
- [ ] Create sheet: `reports_archive`
  - Headers: report_date, report_type, total_properties, total_changes, underperformers_count, summary_data
- [ ] Share workbook with n8n service account email
- [ ] Copy Google Sheet ID for use in workflows

### PriceLabs Setup
- [ ] Verify API access is enabled in PriceLabs account
- [ ] Test API connection with sample GET request
- [ ] Document property IDs for testing
- [ ] Set up template properties (if not already done)
- [ ] Review current pricing strategies

## Phase 2: Core Workflow Development (Week 2-3)

### Error Handler Workflow
- [ ] Create workflow: `PHH_Error_Handler`
- [ ] Add webhook trigger for error events
- [ ] Add error classification logic
- [ ] Add Google Sheets logging node
- [ ] Add email notification for critical errors
- [ ] Test with intentional errors
- [ ] Document error codes and responses

### Main Pricing Engine
- [ ] Create workflow: `PHH_PriceLabs_Main_Engine`
- [ ] Import base structure from `/n8n-workflows/PHH_PriceLabs_Main_Engine_EXAMPLE.json`
- [ ] Update Google Sheet ID in all nodes
- [ ] Update PriceLabs credential references
- [ ] Configure schedule trigger (test: hourly, prod: daily 6am)
- [ ] Test nodes individually:
  - [ ] Load Pricing Config
  - [ ] Fetch PriceLabs Properties
  - [ ] Calculate Performance Metrics
  - [ ] Decision branches
  - [ ] Discount calculations
  - [ ] PriceLabs API updates
  - [ ] Audit logging
- [ ] Test complete workflow with 1-2 test properties
- [ ] Verify audit log entries
- [ ] Verify email notifications

### New Listing Setup Workflow
- [ ] Create workflow: `PHH_New_Listing_Setup`
- [ ] Add webhook trigger
- [ ] Configure webhook URL: `https://[your-n8n-instance]/webhook/phh-new-property`
- [ ] Add webhook signature validation
- [ ] Add property data enrichment from Sheets
- [ ] Add template cloning logic
- [ ] Add peer comparison nodes
- [ ] Add Process Street integration (or email alternative)
- [ ] Test with sample webhook payload from `/example-data/webhook_payload_new_property.json`
- [ ] Verify complete flow from webhook to approval

### Peer Review Handler
- [ ] Create workflow: `PHH_Peer_Review_Handler`
- [ ] Add webhook trigger for approval decisions
- [ ] Configure webhook URL: `https://[your-n8n-instance]/webhook/phh-approval-decision`
- [ ] Add decision routing (approved/rejected)
- [ ] Add PriceLabs activation for approved items
- [ ] Add follow-up task creation for rejections
- [ ] Add status update to Google Sheets
- [ ] Test with sample approval webhook from `/example-data/webhook_payload_approval_decision.json`

## Phase 3: Advanced Features (Week 4)

### Weekly Reporting Workflow
- [ ] Create workflow: `PHH_Weekly_Reporting`
- [ ] Add schedule trigger (Monday 8am)
- [ ] Add audit log retrieval (last 7 days)
- [ ] Add metrics calculation function
- [ ] Add underperformer identification
- [ ] Add CSV generation
- [ ] Add Google Drive upload (optional)
- [ ] Add email report formatting
- [ ] Add Slack notification (optional)
- [ ] Test report generation manually
- [ ] Review report format with team

### Decision Logic Router
- [ ] Create workflow: `PHH_Decision_Logic_Router`
- [ ] Add advanced conditional routing
- [ ] Add weekend vacancy logic
- [ ] Add last-minute discount logic
- [ ] Add consecutive low performance detection
- [ ] Add date-specific pricing overrides
- [ ] Test all decision branches
- [ ] Integrate with Main Engine

### Advanced Features (Optional)
- [ ] Add Slack integration for notifications
- [ ] Add SMS alerts for critical issues
- [ ] Add dashboard webhook for real-time monitoring
- [ ] Add owner portal integration
- [ ] Add multi-channel sync (Airbnb, Booking.com)

## Phase 4: Testing & QA (Week 5)

### Unit Testing
- [ ] Test each workflow independently
- [ ] Test error scenarios for each node
- [ ] Test API timeout handling
- [ ] Test rate limiting scenarios
- [ ] Test data validation and sanitization
- [ ] Test approval workflows
- [ ] Test webhook signature validation

### Integration Testing
- [ ] Test Main Engine → Audit Log → Reporting flow
- [ ] Test New Listing → Review → Activation flow
- [ ] Test Error Handler integration
- [ ] Test concurrent execution scenarios
- [ ] Test with production-like data volume

### Performance Testing
- [ ] Measure execution time for main workflows
- [ ] Test with 50+ properties
- [ ] Identify bottlenecks
- [ ] Optimize slow nodes
- [ ] Add caching where appropriate

### User Acceptance Testing
- [ ] Demonstrate to pricing team
- [ ] Get feedback on approval workflow
- [ ] Review report formats
- [ ] Adjust thresholds based on feedback
- [ ] Document any custom requirements

## Phase 5: Production Deployment (Week 6)

### Pre-Launch
- [ ] Create production Google Sheet (separate from testing)
- [ ] Import production property data
- [ ] Set up production email addresses
- [ ] Configure production schedule triggers
- [ ] Set up monitoring alerts
- [ ] Create runbook for common issues
- [ ] Train team on approval process
- [ ] Create escalation procedures

### Gradual Rollout
- [ ] Week 1: Enable for 10 properties
  - [ ] Monitor daily
  - [ ] Review all price changes
  - [ ] Collect feedback
- [ ] Week 2: Expand to 25 properties
  - [ ] Monitor every 2 days
  - [ ] Review weekly reports
- [ ] Week 3: Full rollout to all properties
  - [ ] Monitor weekly
  - [ ] Review monthly performance

### Post-Launch
- [ ] Set up weekly team review meetings
- [ ] Configure error rate alerts
- [ ] Set up execution monitoring dashboard
- [ ] Document lessons learned
- [ ] Plan Phase 2 features

## Ongoing Maintenance

### Daily
- [ ] Check execution success rate
- [ ] Review critical error logs
- [ ] Monitor pending approvals

### Weekly
- [ ] Review underperformer report
- [ ] Analyze pricing adjustment patterns
- [ ] Check API usage/costs
- [ ] Review team feedback

### Monthly
- [ ] Performance analysis meeting
- [ ] Review and adjust thresholds
- [ ] Security audit (credentials rotation)
- [ ] Cost analysis (API calls, n8n usage)
- [ ] Feature prioritization for next iteration

### Quarterly
- [ ] Major version review
- [ ] Integration updates
- [ ] Competitor analysis
- [ ] Strategy refresh

## Troubleshooting Resources

### Key Documentation
- [ ] Bookmark PriceLabs API documentation
- [ ] Bookmark n8n documentation
- [ ] Bookmark Google Sheets API docs
- [ ] Save this specification for reference

### Support Contacts
- [ ] n8n support (if cloud hosted)
- [ ] PriceLabs support contact
- [ ] Google Cloud Platform support
- [ ] Internal PHH tech team contacts

### Backup & Recovery
- [ ] Export all workflows weekly
- [ ] Backup Google Sheets data
- [ ] Document restore procedures
- [ ] Test restore process quarterly

## Success Metrics

### Track These KPIs
- [ ] Workflow execution success rate (target: >99%)
- [ ] Average execution time (target: <5 minutes for Main Engine)
- [ ] Properties adjusted per week
- [ ] Revenue impact (before/after agent)
- [ ] Manual intervention reduction (target: 80% reduction)
- [ ] Time saved by pricing team (hours/week)
- [ ] Occupancy rate improvements
- [ ] Response time to market changes (hours to adjust)

## Sign-Off

### Implementation Team
- [ ] Tech Lead: _________________ Date: _________
- [ ] Pricing Manager: _________________ Date: _________
- [ ] Operations Manager: _________________ Date: _________

### Go-Live Approval
- [ ] Final UAT passed
- [ ] All critical issues resolved
- [ ] Team training completed
- [ ] Monitoring configured
- [ ] Backup procedures tested
- [ ] Approved for production: _________________ Date: _________
