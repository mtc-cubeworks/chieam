# Testing Guide - Business Logic

This document provides curl commands to test the migrated business logic.

## Prerequisites

1. Start the backend server:
```bash
cd /Users/macbookair/dev_projects/enhanced-ueml/system-generation/eam-fast-api/backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

2. Get an authentication token (if required):
```bash
# Login and get token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'
```

## Asset Management Tests

### Test Asset Workflow - Inspect Asset

```bash
# Create an asset first
curl -X POST http://localhost:8000/api/asset \
  -H "Content-Type: application/json" \
  -d '{
    "asset_tag": "TEST-001",
    "description": "Test Asset",
    "asset_class": "AC-00001",
    "location": "LOC-00001",
    "site": "SITE-00001",
    "department": "DEPT-00001",
    "date_purchased": "2024-01-01"
  }'

# Apply workflow action
curl -X POST http://localhost:8000/api/asset/{asset_id}/workflow \
  -H "Content-Type: application/json" \
  -d '{"action": "inspect_asset"}'
```

### Test Asset Class - Property Inheritance

```bash
# Create parent asset class with properties
curl -X POST http://localhost:8000/api/asset_class \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Parent Class",
    "description": "Parent asset class"
  }'

# Create child asset class (should inherit properties)
curl -X POST http://localhost:8000/api/asset_class \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Child Class",
    "description": "Child asset class",
    "parent_asset_class": "{parent_id}"
  }'

# Verify properties were copied
curl http://localhost:8000/api/asset_class_property?asset_class={child_id}
```

## Work Management Tests

### Test Work Order Workflow

```bash
# Create work order
curl -X POST http://localhost:8000/api/work_order \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Test Work Order",
    "work_order_type": "Corrective Maintenance",
    "due_date": "2024-12-31",
    "priority": "Medium",
    "site": "SITE-00001",
    "department": "DEPT-00001",
    "cost_code": "CC-00001"
  }'

# Approve work order
curl -X POST http://localhost:8000/api/work_order/{wo_id}/workflow \
  -H "Content-Type: application/json" \
  -d '{"action": "approve"}'

# Try to start (should fail if activities not ready)
curl -X POST http://localhost:8000/api/work_order/{wo_id}/workflow \
  -H "Content-Type: application/json" \
  -d '{"action": "start"}'
```

### Test Work Order Activity Workflow

```bash
# Create work order activity
curl -X POST http://localhost:8000/api/work_order_activity \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Test Activity",
    "work_order": "{wo_id}",
    "work_item_type": "Asset",
    "work_item": "{asset_id}",
    "site": "SITE-00001",
    "department": "DEPT-00001"
  }'

# Allocate resources
curl -X POST http://localhost:8000/api/work_order_activity/{woa_id}/workflow \
  -H "Content-Type: application/json" \
  -d '{"action": "allocate"}'

# Start activity
curl -X POST http://localhost:8000/api/work_order_activity/{woa_id}/workflow \
  -H "Content-Type: application/json" \
  -d '{"action": "start_activity"}'

# Complete activity
curl -X POST http://localhost:8000/api/work_order_activity/{woa_id}/workflow \
  -H "Content-Type: application/json" \
  -d '{"action": "complete"}'
```

## Maintenance Management Tests

### Test Maintenance Request Workflow

```bash
# Create maintenance request
curl -X POST http://localhost:8000/api/maintenance_request \
  -H "Content-Type: application/json" \
  -d '{
    "requested_date": "2024-01-01",
    "description": "Test Maintenance",
    "priority": "Medium",
    "asset": "{asset_id}",
    "site": "SITE-00001",
    "department": "DEPT-00001",
    "due_date": "2024-01-15"
  }'

# Submit for approval
curl -X POST http://localhost:8000/api/maintenance_request/{mr_id}/workflow \
  -H "Content-Type: application/json" \
  -d '{"action": "submit_for_approval"}'

# Approve (creates Work Order Activity)
curl -X POST http://localhost:8000/api/maintenance_request/{mr_id}/workflow \
  -H "Content-Type: application/json" \
  -d '{"action": "approve"}'

# Submit for resolution (creates Work Order)
curl -X POST http://localhost:8000/api/maintenance_request/{mr_id}/workflow \
  -H "Content-Type: application/json" \
  -d '{"action": "submit_for_resolution"}'
```

### Test Emergency Maintenance Request

```bash
# Create emergency maintenance request
curl -X POST http://localhost:8000/api/maintenance_request \
  -H "Content-Type: application/json" \
  -d '{
    "requested_date": "2024-01-01",
    "description": "Emergency Repair",
    "priority": "Emergency",
    "asset": "{asset_id}",
    "site": "SITE-00001",
    "department": "DEPT-00001"
  }'

# Submit for emergency (creates Work Order immediately)
curl -X POST http://localhost:8000/api/maintenance_request/{mr_id}/workflow \
  -H "Content-Type: application/json" \
  -d '{"action": "submit_for_emergency"}'
```

## Purchasing and Stores Tests

### Test Purchase Request Workflow

```bash
# Create purchase request
curl -X POST http://localhost:8000/api/purchase_request \
  -H "Content-Type: application/json" \
  -d '{
    "date_requested": "2024-01-01",
    "description": "Test Purchase",
    "site": "SITE-00001",
    "department": "DEPT-00001",
    "due_date": "2024-01-31"
  }'

# Create purchase request line
curl -X POST http://localhost:8000/api/purchase_request_line \
  -H "Content-Type: application/json" \
  -d '{
    "purchase_request": "{pr_id}",
    "item": "ITEM-00001",
    "qty_required": 10
  }'

# Submit for approval
curl -X POST http://localhost:8000/api/purchase_request/{pr_id}/workflow \
  -H "Content-Type: application/json" \
  -d '{"action": "submit_for_approval"}'

# Approve
curl -X POST http://localhost:8000/api/purchase_request/{pr_id}/workflow \
  -H "Content-Type: application/json" \
  -d '{"action": "approve"}'
```

### Test Item Issue Workflow

```bash
# Create item issue
curl -X POST http://localhost:8000/api/item_issue \
  -H "Content-Type: application/json" \
  -d '{
    "issue_type": "WO Parts Issue",
    "work_order_activity": "{woa_id}",
    "issue_to": "EMP-00001",
    "site": "SITE-00001"
  }'

# Create item issue line
curl -X POST http://localhost:8000/api/item_issue_line \
  -H "Content-Type: application/json" \
  -d '{
    "item_issue": "{ii_id}",
    "inventory": "INV-00001",
    "work_order_parts": "{wop_id}",
    "quantity_issued": 5
  }'

# Issue items
curl -X POST http://localhost:8000/api/item_issue/{ii_id}/workflow \
  -H "Content-Type: application/json" \
  -d '{"action": "issue_item"}'
```

### Test Item Return Workflow

```bash
# Create item return
curl -X POST http://localhost:8000/api/item_return \
  -H "Content-Type: application/json" \
  -d '{
    "return_type": "WO Parts Return",
    "work_order_activity": "{woa_id}",
    "returned_by": "EMP-00001"
  }'

# Create item return line
curl -X POST http://localhost:8000/api/item_return_line \
  -H "Content-Type: application/json" \
  -d '{
    "item_return": "{ir_id}",
    "work_order_parts": "{wop_id}",
    "quantity_returned": 2
  }'

# Return items (creates Putaway)
curl -X POST http://localhost:8000/api/item_return/{ir_id}/workflow \
  -H "Content-Type: application/json" \
  -d '{"action": "return_item"}'
```

## Expected Responses

### Success Response
```json
{
  "status": "success",
  "message": "Operation completed successfully"
}
```

### Success with Redirect
```json
{
  "status": "success",
  "message": "Successfully created record",
  "action": "generate_id",
  "path": "/entity/ID-00001"
}
```

### Error Response
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": {
    "field_name": "Error description"
  }
}
```

## Troubleshooting

### Common Issues

1. **"Entity not found"**: Ensure the referenced entity exists
2. **"Workflow state invalid"**: Check current state allows the transition
3. **"Required field missing"**: Verify all required fields are provided
4. **"Insufficient inventory"**: Check inventory quantities before issuing

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
uvicorn app.main:app --reload --port 8000
```
