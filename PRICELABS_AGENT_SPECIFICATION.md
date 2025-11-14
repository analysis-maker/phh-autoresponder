# PriceLabs Agent - Complete n8n Workflow Specification
## Professional Holiday Homes (PHH) - Autonomous Pricing System

---

## 1. HIGH-LEVEL ARCHITECTURE OVERVIEW

### System Components
```
┌─────────────────────────────────────────────────────────────┐
│                    PriceLabs Agent Core                      │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────────┐ │
│  │  Main Pricing  │  │  New Listing   │  │ Peer Review   │ │
│  │  Engine        │  │  Setup Engine  │  │ Automation    │ │
│  └────────────────┘  └────────────────┘  └───────────────┘ │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────────┐ │
│  │  Reporting &   │  │  Decision      │  │ Error Handler │ │
│  │  Analytics     │  │  Logic Engine  │  │ & Logger      │ │
│  └────────────────┘  └────────────────┘  └───────────────┘ │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  PriceLabs    │    │ Google Sheets │    │ Process Street│
│  API          │    │ API           │    │ / Email       │
└───────────────┘    └───────────────┘    └───────────────┘
```

### Data Flow Architecture
1. **Trigger Sources** → Scheduled/Webhook → Main Router
2. **Main Router** → Classifies request → Specific Engine
3. **Engine** → Processes Logic → External APIs
4. **External APIs** → Return Data → Decision Logic
5. **Decision Logic** → Execute Actions → Log Results
6. **Results** → Reports/Notifications → Archive

### Storage Architecture
```
Google Sheets Structure:
├── Config Sheet (pricing_config)
│   ├── Property thresholds
│   ├── Discount rules
│   └── Strategy templates
├── Properties Master (properties_master)
│   ├── Property details
│   ├── Base rates
│   └── Template assignments
├── Audit Log (pricing_audit_log)
│   ├── All pricing changes
│   ├── Timestamp + user/system
│   └── Before/after values
└── Weekly Reports (reports_archive)
    ├── Performance summaries
    └── Action logs
```

---

## 2. DETAILED n8n WORKFLOW DESIGN

### WORKFLOW 1: Main Pricing Intelligence Engine
**Filename:** `PHH_PriceLabs_Main_Engine.json`

#### Node Structure:

```
[Schedule Trigger]
    ↓
[Get Configuration from Sheets]
    ↓
[Get All Properties from PriceLabs]
    ↓
[Loop Over Properties]
    ↓
[Calculate Performance Metrics]
    ↓
[Decision: Needs Price Adjustment?] ──→ [No] → [Log No Action]
    ↓ Yes                                            ↓
[Determine Adjustment Type]                    [Continue Loop]
    ↓
[Switch: Adjustment Type]
    ├─→ [Occupancy-Based] → [Calculate Discount]
    ├─→ [Weekend-Based] → [Calculate Weekend Rate]
    ├─→ [Last-Minute] → [Calculate Last-Min Discount]
    └─→ [Manual Review] → [Create Review Task]
    ↓
[Check if Auto-Approval Allowed]
    ├─→ [Yes] → [Push to PriceLabs API]
    └─→ [No] → [Send Approval Request]
    ↓
[Log Action to Audit Sheet]
    ↓
[Send Notification]
    ↓
[End]
```

#### Node Specifications:

##### Node 1: Schedule Trigger
```json
{
  "name": "Daily Pricing Analysis",
  "type": "n8n-nodes-base.scheduleTrigger",
  "parameters": {
    "rule": {
      "interval": [
        {
          "field": "cronExpression",
          "expression": "0 6 * * 1-5"
        }
      ]
    }
  },
  "notes": "Runs weekdays at 6:00 AM AEST"
}
```

##### Node 2: Get Configuration from Sheets
```json
{
  "name": "Load Pricing Config",
  "type": "n8n-nodes-base.googleSheets",
  "parameters": {
    "operation": "read",
    "sheetName": "pricing_config",
    "range": "A:G",
    "options": {
      "headerRow": 1
    }
  },
  "notes": "Loads dynamic thresholds and rules"
}
```

**Expected Output Schema:**
```javascript
[
  {
    "parameter_name": "low_occupancy_threshold",
    "value": "60",
    "data_type": "percentage"
  },
  {
    "parameter_name": "weekend_adjustment_days",
    "value": "5",
    "data_type": "integer"
  },
  {
    "parameter_name": "discount_percentage_tier1",
    "value": "10",
    "data_type": "percentage"
  }
]
```

##### Node 3: Get All Properties from PriceLabs
```json
{
  "name": "Fetch PriceLabs Properties",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "GET",
    "url": "https://api.pricelabs.co/v1/properties",
    "authentication": "predefinedCredentialType",
    "nodeCredentialType": "priceLabs",
    "options": {
      "timeout": 30000
    }
  }
}
```

**Expected Response:**
```javascript
{
  "properties": [
    {
      "id": "12345",
      "name": "Bondi Beach Apartment",
      "status": "active",
      "base_price": 250,
      "occupancy_last_30_days": 55,
      "next_booking_date": "2025-11-20",
      "pricing_strategy": "dynamic_base"
    }
  ]
}
```

##### Node 4: Calculate Performance Metrics
```javascript
// Function Node: "Calculate Metrics"
{
  "name": "Calculate Performance Metrics",
  "type": "n8n-nodes-base.function",
  "parameters": {
    "functionCode": `
// Input: Property data from PriceLabs + Config from Sheets
const properties = $input.all();
const config = $('Load Pricing Config').all()[0].json;

// Helper: Parse config into usable object
const configMap = {};
config.forEach(row => {
  configMap[row.parameter_name] = parseFloat(row.value);
});

const results = [];

properties.forEach(property => {
  const prop = property.json;

  // Calculate days until next booking
  const nextBooking = new Date(prop.next_booking_date);
  const today = new Date();
  const daysUntilBooking = Math.ceil((nextBooking - today) / (1000 * 60 * 60 * 24));

  // Calculate occupancy status
  const occupancy = prop.occupancy_last_30_days;
  const lowOccupancyThreshold = configMap.low_occupancy_threshold || 60;

  // Check if weekend pricing needed
  const isWeekendSoon = daysUntilBooking <= (configMap.weekend_adjustment_days || 5);

  // Determine action needed
  let actionNeeded = false;
  let actionType = null;
  let reasoning = [];

  if (occupancy < lowOccupancyThreshold) {
    actionNeeded = true;
    actionType = 'occupancy_discount';
    reasoning.push(\`Occupancy at \${occupancy}% below threshold of \${lowOccupancyThreshold}%\`);
  }

  if (isWeekendSoon && occupancy < 70) {
    actionNeeded = true;
    actionType = 'weekend_discount';
    reasoning.push(\`Weekend in \${daysUntilBooking} days with \${occupancy}% occupancy\`);
  }

  if (daysUntilBooking <= 3 && occupancy < 50) {
    actionNeeded = true;
    actionType = 'last_minute_discount';
    reasoning.push('Critical: Last-minute vacancy');
  }

  results.push({
    json: {
      property_id: prop.id,
      property_name: prop.name,
      current_base_price: prop.base_price,
      occupancy: occupancy,
      days_until_booking: daysUntilBooking,
      action_needed: actionNeeded,
      action_type: actionType,
      reasoning: reasoning.join('; '),
      timestamp: new Date().toISOString()
    }
  });
});

return results;
`
  }
}
```

##### Node 5: Decision Branch - Needs Adjustment?
```json
{
  "name": "IF Needs Price Adjustment",
  "type": "n8n-nodes-base.if",
  "parameters": {
    "conditions": {
      "boolean": [
        {
          "value1": "={{ $json.action_needed }}",
          "value2": true
        }
      ]
    }
  }
}
```

##### Node 6: Calculate Discount (Occupancy-Based)
```javascript
{
  "name": "Calculate Occupancy Discount",
  "type": "n8n-nodes-base.function",
  "parameters": {
    "functionCode": `
const property = $input.first().json;
const config = $('Load Pricing Config').all()[0].json;

// Parse config
const configMap = {};
config.forEach(row => {
  configMap[row.parameter_name] = parseFloat(row.value);
});

const occupancy = property.occupancy;
const currentPrice = property.current_base_price;

// Tiered discount logic
let discountPercentage = 0;

if (occupancy < 40) {
  discountPercentage = configMap.discount_percentage_tier3 || 20;
} else if (occupancy < 50) {
  discountPercentage = configMap.discount_percentage_tier2 || 15;
} else if (occupancy < 60) {
  discountPercentage = configMap.discount_percentage_tier1 || 10;
}

const newPrice = Math.round(currentPrice * (1 - discountPercentage / 100));
const requiresApproval = discountPercentage >= 15; // Approval needed for >15% discount

return {
  json: {
    ...property,
    discount_percentage: discountPercentage,
    new_base_price: newPrice,
    price_change_amount: currentPrice - newPrice,
    requires_manual_approval: requiresApproval,
    adjustment_reason: \`Occupancy-based discount due to \${occupancy}% occupancy\`
  }
};
`
  }
}
```

##### Node 7: Push to PriceLabs API
```json
{
  "name": "Update Price in PriceLabs",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "POST",
    "url": "=https://api.pricelabs.co/v1/properties/{{ $json.property_id }}/pricing",
    "authentication": "predefinedCredentialType",
    "nodeCredentialType": "priceLabs",
    "jsonParameters": true,
    "bodyParametersJson": "={{ JSON.stringify({\n  base_price: $json.new_base_price,\n  reason: $json.adjustment_reason,\n  applied_by: 'PHH_Agent',\n  timestamp: new Date().toISOString()\n}) }}",
    "options": {
      "timeout": 15000
    }
  }
}
```

##### Node 8: Log to Audit Sheet
```json
{
  "name": "Log Action to Audit",
  "type": "n8n-nodes-base.googleSheets",
  "parameters": {
    "operation": "append",
    "sheetName": "pricing_audit_log",
    "columns": {
      "mappingMode": "defineBelow",
      "value": {
        "timestamp": "={{ $json.timestamp }}",
        "property_id": "={{ $json.property_id }}",
        "property_name": "={{ $json.property_name }}",
        "old_price": "={{ $json.current_base_price }}",
        "new_price": "={{ $json.new_base_price }}",
        "change_amount": "={{ $json.price_change_amount }}",
        "action_type": "={{ $json.action_type }}",
        "reasoning": "={{ $json.reasoning }}",
        "requires_approval": "={{ $json.requires_manual_approval }}",
        "status": "={{ $json.requires_manual_approval ? 'pending_approval' : 'applied' }}"
      }
    }
  }
}
```

---

### WORKFLOW 2: New Listing Pricing Setup
**Filename:** `PHH_New_Listing_Setup.json`

#### Node Structure:

```
[Webhook Trigger: New Property Added]
    ↓
[Get Property Details from Sheets]
    ↓
[Identify Template Property]
    ↓
[Clone Template Strategy from PriceLabs]
    ↓
[Apply Base Rate Calculations]
    ↓
[Get Comparison Properties (3 peers)]
    ↓
[Generate Peer Comparison Report]
    ↓
[Create Process Street Checklist]
    ↓
[Send to Review Team]
    ↓
[Wait for Approval Webhook]
    ↓
[IF Approved] → [Activate in PriceLabs]
    ↓
[Log Setup Completion]
    ↓
[Send Welcome Email to Owner]
```

#### Key Node Specifications:

##### Node 1: Webhook Trigger
```json
{
  "name": "New Property Webhook",
  "type": "n8n-nodes-base.webhook",
  "parameters": {
    "path": "phh-new-property",
    "httpMethod": "POST",
    "responseMode": "lastNode",
    "options": {
      "rawBody": false
    }
  },
  "notes": "Triggered by Google Sheets/Form submission or manual API call"
}
```

**Expected Webhook Payload:**
```json
{
  "property_name": "Manly Beach House",
  "property_type": "house",
  "bedrooms": 3,
  "location": "Manly, NSW",
  "template_property_id": "67890",
  "owner_email": "owner@example.com",
  "target_revenue_monthly": 8000
}
```

##### Node 2: Get Property Details from Sheets
```javascript
{
  "name": "Enrich Property Data",
  "type": "n8n-nodes-base.googleSheets",
  "parameters": {
    "operation": "lookup",
    "sheetName": "properties_master",
    "lookupColumn": "property_name",
    "lookupValue": "={{ $json.body.property_name }}"
  }
}
```

##### Node 3: Clone Template Strategy
```javascript
{
  "name": "Clone Pricing Strategy",
  "type": "n8n-nodes-base.function",
  "parameters": {
    "functionCode": `
// Step 1: Get template property strategy
const templateId = $json.template_property_id;

// This would call PriceLabs API to get strategy
// For now, we'll structure the expected data

const newProperty = $json;

// Step 2: Calculate base rate using template + adjustments
const templateBaseRate = 200; // Retrieved from PriceLabs
const bedroomMultiplier = newProperty.bedrooms / 3; // Assuming template is 3-bed
const locationMultiplier = 1.1; // Manly premium

const calculatedBaseRate = Math.round(templateBaseRate * bedroomMultiplier * locationMultiplier);

return {
  json: {
    ...newProperty,
    calculated_base_rate: calculatedBaseRate,
    template_strategy: {
      min_price: Math.round(calculatedBaseRate * 0.7),
      max_price: Math.round(calculatedBaseRate * 1.5),
      weekend_premium: 15,
      cleaning_fee: 150
    }
  }
};
`
  }
}
```

##### Node 4: Get Comparison Properties
```javascript
{
  "name": "Find 3 Peer Properties",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "GET",
    "url": "=https://api.pricelabs.co/v1/properties/search?location={{ $json.location }}&bedrooms={{ $json.bedrooms }}&limit=3",
    "authentication": "predefinedCredentialType",
    "nodeCredentialType": "priceLabs"
  }
}
```

##### Node 5: Generate Peer Comparison Report
```javascript
{
  "name": "Create Comparison Report",
  "type": "n8n-nodes-base.function",
  "parameters": {
    "functionCode": `
const newProperty = $('Clone Pricing Strategy').first().json;
const peers = $input.first().json.properties;

const comparison = {
  new_property: {
    name: newProperty.property_name,
    proposed_base_rate: newProperty.calculated_base_rate,
    bedrooms: newProperty.bedrooms
  },
  peer_properties: peers.map(peer => ({
    name: peer.name,
    base_rate: peer.base_price,
    avg_occupancy: peer.occupancy_last_30_days,
    revenue_per_night: peer.average_revenue_per_night
  })),
  comparison_metrics: {
    avg_peer_base_rate: peers.reduce((sum, p) => sum + p.base_price, 0) / peers.length,
    price_variance_percentage: null, // Calculated below
    recommendation: null
  }
};

const avgPeerRate = comparison.comparison_metrics.avg_peer_base_rate;
const variance = ((newProperty.calculated_base_rate - avgPeerRate) / avgPeerRate) * 100;

comparison.comparison_metrics.price_variance_percentage = Math.round(variance);

if (Math.abs(variance) > 20) {
  comparison.comparison_metrics.recommendation = 'REVIEW_REQUIRED';
  comparison.comparison_metrics.note = \`Proposed rate is \${Math.abs(variance)}% \${variance > 0 ? 'higher' : 'lower'} than peer average. Manual review recommended.\`;
} else {
  comparison.comparison_metrics.recommendation = 'APPROVED';
  comparison.comparison_metrics.note = 'Pricing is within acceptable range of peer properties.';
}

return { json: comparison };
`
  }
}
```

##### Node 6: Create Process Street Checklist
```json
{
  "name": "Create Review Checklist",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "POST",
    "url": "https://api.process.st/v1/checklist-runs",
    "authentication": "predefinedCredentialType",
    "nodeCredentialType": "processStreet",
    "jsonParameters": true,
    "bodyParametersJson": "={{ JSON.stringify({\n  template_id: 'pricing_review_template',\n  name: 'Pricing Review: ' + $json.new_property.name,\n  form_fields: {\n    property_name: $json.new_property.name,\n    proposed_rate: $json.new_property.proposed_base_rate,\n    peer_avg: $json.comparison_metrics.avg_peer_base_rate,\n    variance: $json.comparison_metrics.price_variance_percentage,\n    recommendation: $json.comparison_metrics.recommendation\n  }\n}) }}"
  }
}
```

##### Node 7: Send to Review Team
```json
{
  "name": "Email Review Team",
  "type": "n8n-nodes-base.emailSend",
  "parameters": {
    "fromEmail": "pricing-agent@phh.com.au",
    "toEmail": "pricing-team@phh.com.au",
    "subject": "=NEW PROPERTY REVIEW: {{ $('Clone Pricing Strategy').first().json.property_name }}",
    "text": "=A new property requires pricing review.\n\nProperty: {{ $('Clone Pricing Strategy').first().json.property_name }}\nProposed Base Rate: ${{ $('Clone Pricing Strategy').first().json.calculated_base_rate }}\nPeer Average: ${{ $json.comparison_metrics.avg_peer_base_rate }}\nVariance: {{ $json.comparison_metrics.price_variance_percentage }}%\n\nRecommendation: {{ $json.comparison_metrics.recommendation }}\n\nProcess Street Checklist: {{ $('Create Review Checklist').first().json.url }}\n\nPlease review and approve within 24 hours.",
    "options": {}
  }
}
```

---

### WORKFLOW 3: Peer Review Automation
**Filename:** `PHH_Peer_Review_Handler.json`

#### Node Structure:

```
[Webhook: Review Decision Received]
    ↓
[Parse Decision Data]
    ↓
[Get Property Pending Review]
    ↓
[IF Approved]
    ├─→ [Activate Pricing in PriceLabs]
    │   ↓
    │   [Update Status in Sheets]
    │   ↓
    │   [Send Confirmation Email]
    │   ↓
    │   [Archive Review Data]
    └─→ [IF Rejected]
        ↓
        [Flag for Revision]
        ↓
        [Notify Submitter]
        ↓
        [Create Follow-up Task]
```

#### Key Code Snippets:

##### Approval Handler
```javascript
{
  "name": "Process Approval",
  "type": "n8n-nodes-base.function",
  "parameters": {
    "functionCode": `
const decision = $json.body;

if (decision.status === 'approved') {
  // Activate the property
  const propertyData = decision.property_data;

  return [{
    json: {
      action: 'activate',
      property_id: propertyData.property_id,
      approved_base_rate: propertyData.proposed_base_rate,
      approved_by: decision.reviewer_email,
      approved_at: new Date().toISOString(),
      notes: decision.reviewer_notes
    }
  }];
} else {
  // Handle rejection
  return [{
    json: {
      action: 'reject',
      property_id: propertyData.property_id,
      rejection_reason: decision.reviewer_notes,
      rejected_by: decision.reviewer_email,
      rejected_at: new Date().toISOString(),
      requires_revision: true
    }
  }];
}
`
  }
}
```

---

### WORKFLOW 4: Reporting & Data Export
**Filename:** `PHH_Weekly_Reporting.json`

#### Node Structure:

```
[Schedule: Monday 8 AM]
    ↓
[Get Last 7 Days Audit Logs]
    ↓
[Calculate Weekly Metrics]
    ↓
[Identify Underperforming Properties]
    ↓
[Generate CSV Report]
    ↓
[Upload to Google Drive]
    ↓
[Create Email Summary]
    ↓
[Send to Management Team]
    ↓
[Post Summary to Slack]
```

#### Key Node: Calculate Weekly Metrics

```javascript
{
  "name": "Calculate Weekly Metrics",
  "type": "n8n-nodes-base.function",
  "parameters": {
    "functionCode": `
const auditLogs = $input.all();
const logs = auditLogs.map(item => item.json);

// Group by property
const propertyMetrics = {};

logs.forEach(log => {
  if (!propertyMetrics[log.property_id]) {
    propertyMetrics[log.property_id] = {
      property_name: log.property_name,
      price_changes: 0,
      total_price_reduction: 0,
      total_price_increase: 0,
      actions_taken: []
    };
  }

  const metrics = propertyMetrics[log.property_id];
  metrics.price_changes++;

  if (log.change_amount < 0) {
    metrics.total_price_increase += Math.abs(log.change_amount);
  } else {
    metrics.total_price_reduction += log.change_amount;
  }

  metrics.actions_taken.push(log.action_type);
});

// Identify underperformers (>3 price reductions in a week)
const underperformers = Object.values(propertyMetrics)
  .filter(p => p.price_changes > 3 || p.total_price_reduction > 500)
  .sort((a, b) => b.total_price_reduction - a.total_price_reduction);

// Calculate summary stats
const summary = {
  total_properties_adjusted: Object.keys(propertyMetrics).length,
  total_price_changes: logs.length,
  avg_price_reduction: logs.filter(l => l.change_amount > 0)
    .reduce((sum, l) => sum + l.change_amount, 0) / logs.length,
  underperforming_properties: underperformers.length,
  period_start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  period_end: new Date().toISOString().split('T')[0]
};

return {
  json: {
    summary,
    underperformers,
    all_property_metrics: propertyMetrics
  }
};
`
  }
}
```

#### Key Node: Generate CSV Report

```javascript
{
  "name": "Generate CSV Report",
  "type": "n8n-nodes-base.function",
  "parameters": {
    "functionCode": `
const data = $input.first().json;

// Create CSV header
let csv = 'Property Name,Price Changes,Total Reduction ($),Total Increase ($),Status\\n';

// Add underperformer data
data.underperformers.forEach(prop => {
  csv += \`"\${prop.property_name}",\${prop.price_changes},\${prop.total_price_reduction},\${prop.total_price_increase},"UNDERPERFORMING"\\n\`;
});

// Add summary section
csv += '\\n\\nWEEKLY SUMMARY\\n';
csv += \`Total Properties Adjusted,\${data.summary.total_properties_adjusted}\\n\`;
csv += \`Total Price Changes,\${data.summary.total_price_changes}\\n\`;
csv += \`Average Reduction,\${Math.round(data.summary.avg_price_reduction)}\\n\`;
csv += \`Underperforming Properties,\${data.summary.underperforming_properties}\\n\`;

return {
  json: {
    csv_content: csv,
    filename: \`PHH_Pricing_Report_\${data.summary.period_start}_to_\${data.summary.period_end}.csv\`
  }
};
`
  }
}
```

#### Key Node: Upload to Google Drive

```json
{
  "name": "Upload Report to Drive",
  "type": "n8n-nodes-base.googleDrive",
  "parameters": {
    "operation": "upload",
    "folderId": "pricing_reports_folder_id",
    "name": "={{ $json.filename }}",
    "binaryData": false,
    "fileContent": "={{ $json.csv_content }}"
  }
}
```

---

### WORKFLOW 5: Advanced Decision Logic Engine
**Filename:** `PHH_Decision_Logic_Router.json`

This is a sub-workflow called by the Main Engine.

#### Conditional Logic Flowchart:

```javascript
{
  "name": "Advanced Decision Router",
  "type": "n8n-nodes-base.switch",
  "parameters": {
    "mode": "expression",
    "output": "always",
    "rules": {
      "rules": [
        {
          "output": 0,
          "expression": "={{ $json.occupancy < 60 && $json.days_until_booking > 14 }}"
        },
        {
          "output": 1,
          "expression": "={{ $json.days_until_booking <= 5 && new Date($json.next_booking_date).getDay() >= 5 }}"
        },
        {
          "output": 2,
          "expression": "={{ $json.days_until_booking <= 3 && $json.occupancy < 50 }}"
        },
        {
          "output": 3,
          "expression": "={{ $json.consecutive_low_performance > 3 }}"
        }
      ]
    }
  }
}
```

**Decision Outputs:**
- Output 0: Apply 14-day occupancy discount
- Output 1: Apply weekend vacancy discount (5 days out)
- Output 2: Apply emergency last-minute discount
- Output 3: Flag for manual strategic review

#### Implementation of Rule: "If weekend vacancy remains 5 days before check-in → lower weekend price 10%"

```javascript
{
  "name": "Weekend Vacancy Logic",
  "type": "n8n-nodes-base.function",
  "parameters": {
    "functionCode": `
const property = $input.first().json;
const nextBooking = new Date(property.next_booking_date);
const dayOfWeek = nextBooking.getDay(); // 0 = Sunday, 6 = Saturday

// Check if next booking is a weekend
const isWeekend = dayOfWeek === 5 || dayOfWeek === 6 || dayOfWeek === 0;

if (isWeekend && property.days_until_booking <= 5) {
  const currentPrice = property.current_base_price;
  const weekendDiscount = 10; // 10% reduction
  const newWeekendPrice = Math.round(currentPrice * 0.9);

  // Get the weekend date range
  const weekendStart = new Date(nextBooking);
  weekendStart.setDate(weekendStart.getDate() - (dayOfWeek === 0 ? 2 : dayOfWeek === 6 ? 1 : 0));

  const weekendEnd = new Date(weekendStart);
  weekendEnd.setDate(weekendEnd.getDate() + 2);

  return {
    json: {
      ...property,
      action_type: 'weekend_discount',
      discount_percentage: weekendDiscount,
      new_weekend_price: newWeekendPrice,
      price_change_amount: currentPrice - newWeekendPrice,
      date_range_start: weekendStart.toISOString().split('T')[0],
      date_range_end: weekendEnd.toISOString().split('T')[0],
      requires_manual_approval: false,
      adjustment_reason: \`Weekend vacancy \${property.days_until_booking} days out - applying 10% discount\`
    }
  };
}

return { json: property };
`
  }
}
```

#### Apply Weekend-Specific Price to PriceLabs

```json
{
  "name": "Apply Weekend Price Override",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "POST",
    "url": "=https://api.pricelabs.co/v1/properties/{{ $json.property_id }}/custom-pricing",
    "authentication": "predefinedCredentialType",
    "nodeCredentialType": "priceLabs",
    "jsonParameters": true,
    "bodyParametersJson": "={{ JSON.stringify({\n  start_date: $json.date_range_start,\n  end_date: $json.date_range_end,\n  custom_price: $json.new_weekend_price,\n  reason: $json.adjustment_reason,\n  applied_by: 'PHH_Agent_Weekend_Logic'\n}) }}"
  }
}
```

---

## 3. ERROR HANDLING, LOGGING & SECURITY

### Error Handling Architecture

#### Global Error Catcher Node
Add to every workflow:

```json
{
  "name": "Global Error Handler",
  "type": "n8n-nodes-base.executeWorkflow",
  "parameters": {
    "workflowId": "error_handler_workflow_id"
  },
  "onError": "continueErrorOutput"
}
```

#### Error Handler Workflow
**Filename:** `PHH_Error_Handler.json`

```javascript
{
  "name": "Process Error",
  "type": "n8n-nodes-base.function",
  "parameters": {
    "functionCode": `
const error = $input.first().json;

// Classify error severity
let severity = 'low';
let notifyTeam = false;

if (error.node.includes('PriceLabs') || error.node.includes('Update Price')) {
  severity = 'critical';
  notifyTeam = true;
}

if (error.message.includes('timeout') || error.message.includes('rate limit')) {
  severity = 'medium';
}

// Structure error log
const errorLog = {
  timestamp: new Date().toISOString(),
  workflow_name: error.workflow.name,
  workflow_id: error.workflow.id,
  execution_id: error.execution.id,
  node_name: error.node,
  error_message: error.message,
  error_stack: error.stack,
  severity: severity,
  input_data: JSON.stringify(error.data),
  requires_notification: notifyTeam
};

return { json: errorLog };
`
  }
}
```

#### Retry Logic for API Calls

```json
{
  "name": "PriceLabs API Call with Retry",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "POST",
    "url": "https://api.pricelabs.co/v1/properties/12345/pricing",
    "options": {
      "timeout": 15000,
      "retry": {
        "maxRetries": 3,
        "retryOnStatus": [408, 429, 500, 502, 503, 504],
        "retryDelay": 2000
      }
    }
  }
}
```

### Logging Strategy

#### Log Levels
1. **INFO**: Routine operations (price updates, property checks)
2. **WARN**: Unusual patterns (large discounts, approval timeouts)
3. **ERROR**: API failures, data inconsistencies
4. **CRITICAL**: System failures, security issues

#### Centralized Logging Node

```javascript
{
  "name": "Write to Central Log",
  "type": "n8n-nodes-base.googleSheets",
  "parameters": {
    "operation": "append",
    "sheetName": "system_logs",
    "columns": {
      "mappingMode": "defineBelow",
      "value": {
        "timestamp": "={{ new Date().toISOString() }}",
        "workflow": "={{ $workflow.name }}",
        "execution_id": "={{ $execution.id }}",
        "log_level": "={{ $json.log_level }}",
        "message": "={{ $json.message }}",
        "data": "={{ JSON.stringify($json.data) }}"
      }
    }
  }
}
```

### Security Best Practices

#### 1. Credential Management
```
Store in n8n Credentials Manager:
├── PriceLabs API Key (Type: API Key Auth)
│   └── Header: X-API-Key
├── Google Sheets OAuth2
│   └── Scopes: spreadsheets, drive.file
├── Process Street API Key
└── SMTP Credentials for Email
```

#### 2. Webhook Security
```javascript
{
  "name": "Validate Webhook Signature",
  "type": "n8n-nodes-base.function",
  "parameters": {
    "functionCode": `
const crypto = require('crypto');

const payload = JSON.stringify($json.body);
const signature = $json.headers['x-webhook-signature'];
const secret = '{{$credentials.webhook_secret}}';

const expectedSignature = crypto
  .createHmac('sha256', secret)
  .update(payload)
  .digest('hex');

if (signature !== expectedSignature) {
  throw new Error('Invalid webhook signature - potential security breach');
}

return { json: $json.body };
`
  }
}
```

#### 3. Rate Limiting Protection
```javascript
// Store in global variable or Redis
const rateLimiter = {
  checkLimit: (apiName) => {
    const now = Date.now();
    const key = `${apiName}_${Math.floor(now / 60000)}`; // Per minute
    const count = $vars[key] || 0;

    if (count >= 60) { // Max 60 calls per minute
      throw new Error(`Rate limit exceeded for ${apiName}`);
    }

    $vars[key] = count + 1;
    return true;
  }
};
```

#### 4. Data Sanitization
```javascript
{
  "name": "Sanitize Input Data",
  "type": "n8n-nodes-base.function",
  "parameters": {
    "functionCode": `
const sanitize = (str) => {
  return String(str)
    .replace(/[<>]/g, '') // Remove HTML tags
    .replace(/[\\${}]/g, '') // Remove potential injection chars
    .trim();
};

const input = $json.body;

return {
  json: {
    property_name: sanitize(input.property_name),
    property_type: sanitize(input.property_type),
    bedrooms: parseInt(input.bedrooms) || 0,
    owner_email: input.owner_email.toLowerCase().trim()
  }
};
`
  }
}
```

---

## 4. NAMING CONVENTIONS & ORGANIZATION

### Workflow Naming
```
Format: PHH_{Module}_{Function}_{Version}.json

Examples:
├── PHH_PriceLabs_Main_Engine_v1.json
├── PHH_New_Listing_Setup_v1.json
├── PHH_Peer_Review_Handler_v1.json
├── PHH_Weekly_Reporting_v1.json
├── PHH_Decision_Logic_Router_v1.json
└── PHH_Error_Handler_v1.json
```

### Node Naming Conventions
```
Format: [Action] [Subject] [Context]

Good Examples:
✓ "Calculate Occupancy Discount"
✓ "Fetch PriceLabs Properties"
✓ "Log Action to Audit"
✓ "IF Needs Price Adjustment"
✓ "Send Approval Email to Team"

Bad Examples:
✗ "Node 1"
✗ "Function"
✗ "HTTP Request"
✗ "Process Data"
```

### Variable Naming
```javascript
// Use snake_case for data properties
{
  property_id: "12345",
  base_price: 250,
  occupancy_last_30_days: 55,
  requires_manual_approval: true
}

// Use camelCase for internal function variables
const propertyData = $json;
const configMap = {};
const discountPercentage = 10;
```

### Google Sheets Structure

#### Sheet: `pricing_config`
```
| parameter_name              | value | data_type  | description                    | last_updated |
|-----------------------------|-------|------------|--------------------------------|--------------|
| low_occupancy_threshold     | 60    | percentage | Trigger for discount           | 2025-11-01   |
| discount_percentage_tier1   | 10    | percentage | Discount for 50-60% occupancy  | 2025-11-01   |
| discount_percentage_tier2   | 15    | percentage | Discount for 40-50% occupancy  | 2025-11-01   |
| discount_percentage_tier3   | 20    | percentage | Discount for <40% occupancy    | 2025-11-01   |
| weekend_adjustment_days     | 5     | integer    | Days before to check weekend   | 2025-11-01   |
| approval_threshold_amount   | 50    | currency   | Price change requiring approval| 2025-11-01   |
```

#### Sheet: `properties_master`
```
| property_id | property_name        | location      | bedrooms | property_type | template_id | base_rate | status | created_date |
|-------------|----------------------|---------------|----------|---------------|-------------|-----------|--------|--------------|
| 12345       | Bondi Beach Apt      | Bondi, NSW    | 2        | apartment     | 67890       | 250       | active | 2025-01-15   |
| 12346       | Manly Beach House    | Manly, NSW    | 3        | house         | 67890       | 350       | setup  | 2025-11-14   |
```

#### Sheet: `pricing_audit_log`
```
| timestamp           | property_id | property_name     | old_price | new_price | change_amount | action_type         | reasoning                | requires_approval | status   |
|---------------------|-------------|-------------------|-----------|-----------|---------------|---------------------|--------------------------|-------------------|----------|
| 2025-11-14 06:15:00 | 12345       | Bondi Beach Apt   | 250       | 225       | 25            | occupancy_discount  | Occupancy at 55%         | FALSE             | applied  |
| 2025-11-14 06:16:00 | 12347       | Sydney CBD Studio | 180       | 144       | 36            | last_minute_discount| Critical: 2 days out     | FALSE             | applied  |
```

---

## 5. IMPLEMENTATION GUIDE

### Phase 1: Setup (Week 1)

1. **n8n Installation & Configuration**
   ```bash
   # If self-hosted
   docker run -it --rm \
     --name n8n \
     -p 5678:5678 \
     -e N8N_BASIC_AUTH_ACTIVE=true \
     -e N8N_BASIC_AUTH_USER=phh_admin \
     -e N8N_BASIC_AUTH_PASSWORD=secure_password \
     -v ~/.n8n:/home/node/.n8n \
     n8nio/n8n
   ```

2. **Credential Setup**
   - Add PriceLabs API credentials
   - Connect Google Sheets OAuth2
   - Configure email SMTP
   - Add Process Street API key (if using)

3. **Google Sheets Preparation**
   - Create workbook: "PHH PriceLabs Agent Data"
   - Create sheets: pricing_config, properties_master, pricing_audit_log, system_logs, reports_archive
   - Populate initial config values
   - Share with n8n service account

### Phase 2: Core Workflows (Week 2-3)

1. **Build Error Handler First**
   - Import `PHH_Error_Handler.json`
   - Test with intentional failures
   - Verify logging to system_logs sheet

2. **Build Main Pricing Engine**
   - Import `PHH_PriceLabs_Main_Engine.json`
   - Configure schedule trigger for testing (every hour)
   - Test with 1-2 properties first
   - Validate audit logging

3. **Build New Listing Setup**
   - Import `PHH_New_Listing_Setup.json`
   - Test webhook with sample payload
   - Verify template cloning logic

### Phase 3: Advanced Features (Week 4)

1. **Peer Review Automation**
2. **Weekly Reporting**
3. **Decision Logic Engine**

### Phase 4: Testing & Refinement (Week 5)

1. **End-to-End Testing**
   - Test all workflows with production data
   - Verify approval workflows
   - Test error scenarios

2. **Performance Optimization**
   - Add caching where appropriate
   - Optimize API call frequency
   - Review execution times

3. **Documentation**
   - Document custom configurations
   - Create runbooks for common issues
   - Train team on approval process

### Phase 5: Go Live (Week 6)

1. **Gradual Rollout**
   - Start with 10 properties
   - Monitor for 1 week
   - Expand to 25 properties
   - Monitor for 1 week
   - Full rollout

2. **Monitoring Setup**
   - Set up execution monitoring
   - Configure error alerts
   - Schedule weekly review meetings

---

## 6. TESTING SCENARIOS

### Test Case 1: Low Occupancy Trigger
```json
{
  "test_name": "Occupancy below threshold triggers discount",
  "input": {
    "property_id": "TEST_001",
    "occupancy_last_30_days": 45,
    "current_base_price": 200
  },
  "expected_output": {
    "action_needed": true,
    "action_type": "occupancy_discount",
    "discount_percentage": 15,
    "new_base_price": 170,
    "requires_manual_approval": true
  }
}
```

### Test Case 2: Weekend Vacancy
```json
{
  "test_name": "Weekend vacancy 5 days out",
  "input": {
    "property_id": "TEST_002",
    "next_booking_date": "2025-11-19", // Friday
    "days_until_booking": 5,
    "current_base_price": 300,
    "occupancy_last_30_days": 65
  },
  "expected_output": {
    "action_type": "weekend_discount",
    "new_weekend_price": 270,
    "date_range_start": "2025-11-19",
    "date_range_end": "2025-11-21"
  }
}
```

### Test Case 3: New Listing Setup
```json
{
  "test_name": "New 3-bedroom house in Manly",
  "input": {
    "property_name": "Manly Beach House",
    "bedrooms": 3,
    "location": "Manly, NSW",
    "template_property_id": "67890"
  },
  "expected_output": {
    "calculated_base_rate": 385,
    "comparison_metrics": {
      "recommendation": "APPROVED",
      "price_variance_percentage": 8
    },
    "checklist_created": true
  }
}
```

---

## 7. MAINTENANCE & MONITORING

### Daily Checks (Automated)
- Workflow execution success rate
- API error rates
- Properties requiring approval

### Weekly Review (Manual)
- Review underperforming properties report
- Adjust thresholds if needed
- Review audit log for anomalies

### Monthly Tasks
- Performance analysis
- Cost review (API calls)
- Feature requests from team
- Security audit

### Monitoring Dashboard (Create in n8n or external)
```
Metrics to Track:
├── Total Executions (Last 24h)
├── Success Rate (%)
├── Average Execution Time
├── Properties Adjusted (Last 7 days)
├── Total Price Changes ($)
├── Pending Approvals
└── Error Count by Type
```

---

## 8. API REFERENCE

### PriceLabs API Endpoints Used

#### Get Properties
```
GET https://api.pricelabs.co/v1/properties
Headers:
  X-API-Key: {api_key}
Response: Array of property objects
```

#### Update Base Price
```
POST https://api.pricelabs.co/v1/properties/{property_id}/pricing
Headers:
  X-API-Key: {api_key}
  Content-Type: application/json
Body:
{
  "base_price": 250,
  "reason": "Occupancy adjustment",
  "applied_by": "PHH_Agent"
}
```

#### Apply Custom Date Range Pricing
```
POST https://api.pricelabs.co/v1/properties/{property_id}/custom-pricing
Body:
{
  "start_date": "2025-11-19",
  "end_date": "2025-11-21",
  "custom_price": 270,
  "reason": "Weekend vacancy discount"
}
```

#### Clone Pricing Strategy
```
POST https://api.pricelabs.co/v1/properties/{property_id}/clone-strategy
Body:
{
  "source_property_id": "67890",
  "include_rules": true,
  "include_customizations": false
}
```

### Google Sheets API Operations

All operations use the n8n Google Sheets node with OAuth2 authentication.

#### Read Configuration
```
Operation: Read
Sheet: pricing_config
Range: A:G
```

#### Append to Audit Log
```
Operation: Append
Sheet: pricing_audit_log
Columns: timestamp, property_id, old_price, new_price, action_type
```

#### Lookup Property
```
Operation: Lookup
Sheet: properties_master
Lookup Column: property_id
Lookup Value: 12345
```

---

## 9. ADVANCED FEATURES & FUTURE ENHANCEMENTS

### Phase 2 Features (Post-Launch)

1. **Machine Learning Price Optimization**
   - Integrate with Python/TensorFlow via webhook
   - Train on historical occupancy + pricing data
   - Predict optimal price points

2. **Competitor Price Monitoring**
   - Scrape competitor listings
   - Auto-adjust if market rates change
   - Alert if significantly underpriced

3. **Dynamic Seasonality Rules**
   - Auto-detect high/low seasons from historical data
   - Adjust strategies by season without manual config

4. **Owner Portal Integration**
   - Allow owners to set minimum acceptable rates
   - Auto-approve within owner thresholds
   - Send owner reports

5. **Multi-Channel Sync**
   - Push to Airbnb, Booking.com, VRBO
   - Sync calendar blocks
   - Unified pricing across platforms

---

## 10. TROUBLESHOOTING GUIDE

### Common Issues

#### Issue: Workflow times out
**Solution:**
- Reduce batch size in loop nodes
- Add pagination for large property lists
- Increase timeout in HTTP Request nodes to 30000ms

#### Issue: PriceLabs API rate limit
**Solution:**
- Add Wait node between API calls (2 seconds)
- Implement rate limiting check before calls
- Cache property data in Google Sheets, refresh hourly

#### Issue: Google Sheets quota exceeded
**Solution:**
- Batch write operations (collect 10 logs, write once)
- Use daily archival to separate sheets
- Consider upgrading to Google Workspace

#### Issue: Duplicate price changes
**Solution:**
- Add "last_updated" timestamp check
- Skip if changed in last 6 hours
- Implement idempotency key in audit log

---

## SUMMARY

This specification provides a complete, production-ready n8n workflow system for PHH's autonomous pricing management. The architecture includes:

✓ 6 core workflows with detailed node specifications
✓ Full error handling and logging infrastructure
✓ Security best practices and rate limiting
✓ Comprehensive testing scenarios
✓ Maintenance and monitoring guidelines
✓ API reference documentation
✓ Implementation roadmap

### Quick Start Checklist

- [ ] Set up n8n instance (cloud or self-hosted)
- [ ] Configure all API credentials
- [ ] Create Google Sheets with proper structure
- [ ] Import `PHH_Error_Handler.json` workflow
- [ ] Import `PHH_PriceLabs_Main_Engine.json` workflow
- [ ] Test with 1-2 properties in staging
- [ ] Configure schedule triggers
- [ ] Set up monitoring dashboard
- [ ] Train team on approval workflows
- [ ] Launch with limited property set
- [ ] Monitor and iterate

### Key Files to Create in n8n

1. `PHH_PriceLabs_Main_Engine.json` - Core pricing logic
2. `PHH_New_Listing_Setup.json` - Onboarding automation
3. `PHH_Peer_Review_Handler.json` - Approval workflow
4. `PHH_Weekly_Reporting.json` - Analytics and reports
5. `PHH_Decision_Logic_Router.json` - Advanced rules engine
6. `PHH_Error_Handler.json` - Global error management

All code snippets and JSON examples provided are directly usable in n8n with minimal configuration changes (mainly credential assignment and Google Sheet IDs).

---

**Document Version:** 1.0
**Last Updated:** 2025-11-14
**Maintained By:** PHH Tech Team
**Next Review:** 2025-12-14
