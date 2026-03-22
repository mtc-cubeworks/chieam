// Auto-generated TypeScript types from entity metadata
// Do not edit manually - run: python -m app.forge generate-types

export interface BaseEntity {
  id: string
  created_at: string
  updated_at: string
}

export interface Manufacturer extends BaseEntity {
  company_name: string
  email?: string
}

export interface Role extends BaseEntity {
  name: string
  description?: string
  is_active: boolean
}

export interface User extends BaseEntity {
  username: string
  email: string
  full_name?: string
  hashed_password: string
  is_active: boolean
  is_superuser: boolean
}

export interface Department extends BaseEntity {
  department_name: string
  department_code: string
  site: string
  site_name?: string
  department_manager?: string
  default_cost_code: string
  overhead_method?: string
  overhead_percent?: number
  overhead_rp_hour?: number
  overhead_expense_account?: string
  labor_expense_account_overwrite?: string
}

export interface Model extends BaseEntity {
  model_name: string
  manufacturer: string
  manufacturer_name?: string
}

export interface Site extends BaseEntity {
  site_name: string
  site_code: string
  organization: string
  organization_name?: string
  default_cost_code?: string
  site_manager?: string
  location?: string
  location_name?: string
}

export interface UnitOfMeasure extends BaseEntity {
  name?: string
  short_name?: string
}

export interface Employee extends BaseEntity {
  user: string
  employee_name?: string
  position: string
  attachments?: unknown
}

export interface Project extends BaseEntity {
  name?: string
  description?: string
  start_date?: string
  end_date?: string
  status: string
}

export interface InventoryAdjustment extends BaseEntity {
  workflow_state?: string
  reference_doctype?: string
  posting_datetime?: string
  location: string
  store: string
  site: string
  cost_center?: string
  remarks?: string
}

export interface InventoryAdjustmentLine extends BaseEntity {
  inventory_adjustment: string
  inventory?: string
  item: string
  asset_tag?: string
  serial_nos?: string
  bin?: string
  zone?: string
  uom?: string
  current_qty?: number
  adjusted_qty: number
  current_rate?: number
  delta_value: number
  inventory_adjustment_account?: string
  inventory_account?: string
}

export interface Putaway extends BaseEntity {
  putaway_type: string
  source_data_repair?: string
  source_data_parts_return?: string
  source_data_asset?: string
  item: string
  serial_number?: string
  qty: number
  site: string
  store?: string
  bin?: string
  zone?: string
}

export interface RfqLog extends BaseEntity {
  purchase_request?: string
  generated_by?: string
  date_issue?: string
  requestor?: string
  due_date?: string
  remarks?: string
}

export interface ItemReturnLine extends BaseEntity {
  item_return: string
  work_order_parts?: string
  work_order_equipment?: string
  item: string
  quantity_returned: number
  unit_cost?: number
}

export interface Bin extends BaseEntity {
  rack_name?: string
  shelf_name?: string
  bin_name?: string
  store?: string
  store_name?: string
  site?: string
}

export interface PurchaseReturn extends BaseEntity {
  inventory?: string
  serial_number?: string
  item?: string
  unit_of_measure?: string
  date_returned?: string
  quantity_returned?: number
  site?: string
  department?: string
  cost_code?: string
}

export interface Zone extends BaseEntity {
  zone_name?: string
  store?: string
  store_name?: string
  site?: string
}

export interface Transfer extends BaseEntity {
  transfer_type: string
  moved_by: string
  date_moved: string
  work_order_activity?: string
  inventory?: string
  labor?: string
  equipment?: string
  item_to_transfer?: string
  purchase_request_line?: string
  site: string
  from_location?: string
  from_store?: string
  from_bin?: string
  from_zone?: string
  to_location?: string
  to_vendor?: string
  to_store?: string
  to_bin?: string
  to_zone?: string
}

export interface ItemIssueLine extends BaseEntity {
  item_issue: string
  work_order_parts?: string
  work_order_equipment?: string
  inventory: string
  item_name?: string
  store?: string
  bin?: string
  zone?: string
  quantity_issued: number
  unit_cost?: number
}

export interface Inspection extends BaseEntity {
  inspection_date: string
  inspector: string
  site: string
  inventory: string
  inspection_result: string
  action_required?: string
}

export interface Item extends BaseEntity {
  name?: string
  description?: string
}

export interface Inventory extends BaseEntity {
  name?: string
  description?: string
}

export interface TransferReceipt extends BaseEntity {
  transfer_request: string
  inventory?: string
  unit_of_measure?: string
  date_received: string
  receiving_location: string
  site: string
}

export interface ReasonCode extends BaseEntity {
  code?: string
  description?: string
  movement_type?: string
  default_debit_account?: string
  default_credit_account?: string
  attachments?: unknown
  approval_threshold?: string
}

export interface PurchaseRequestLine extends BaseEntity {
  workflow_state?: string
  purchase_request: string
  financial_asset_number?: string
  row_no?: number
  item: string
  item_name?: string
  item_description?: string
  unit_of_measure?: string
  site: string
  department: string
  account_code?: string
  cost_code?: string
  vendor?: string
  po_num?: string
  date_required?: string
  qty_required: number
  qty_received?: number
  total_line_amount?: number
  unit_cost?: number
  base_currency?: string
  base_currency_unit?: number
  base_currency_line_amount?: number
  conversion_factor?: number
}

export interface StockCountTask extends BaseEntity {
  stock_count?: string
  assigned_to?: string
  bin?: string
  submitted_at?: string
  site?: string
}

export interface PurchaseReceipt extends BaseEntity {
  purchase_request_line: string
  pr_row_no?: number
  is_received?: boolean
  item?: string
  quantity_received: number
  date_received: string
  receiving_location: string
  site: string
  department: string
  generated_inventory?: boolean
  account_code?: string
  attachments?: unknown
}

export interface Currency extends BaseEntity {
  currency_name: string
  symbol?: string
  conversion_factor?: number
  active?: boolean
}

export interface ItemIssue extends BaseEntity {
  workflow_state?: string
  issue_type: string
  issue_to: string
  date_issued: string
  work_order_activity?: string
  site: string
  department: string
  cost_code: string
}

export interface StockLedgerEntry extends BaseEntity {
  item?: string
  serial_no?: string
  store?: string
  bin?: string
  posting_datetime?: string
  qty_in?: number
  qty_out?: number
  value_in?: number
  value_out?: number
  balance_qty?: number
  balance_value?: number
  voucher_type?: string
  voucher_no?: string
  site?: string
}

export interface ItemReturn extends BaseEntity {
  workflow_state?: string
  return_type: string
  returned_by: string
  date_returned: string
  work_order_activity: string
  site: string
  department: string
  cost_code: string
}

export interface StockCount extends BaseEntity {
  workflow_state?: string
  store: string
  site: string
  method: string
  basis: string
  abc_code?: string
  freeze_policy: string
  snapshot_at?: string
  attach_csv?: unknown
}

export interface Vendor extends BaseEntity {
  vendor_name?: string
  site?: string
}

export interface PurchaseRequest extends BaseEntity {
  workflow_state?: string
  date_requested: string
  pr_description: string
  requestor: string
  requestor_name?: string
  due_date?: string
  work_activity_id?: string
  maintenance_request?: string
  reject_reason?: string
  site: string
  department: string
  cost_code?: string
}

export interface Store extends BaseEntity {
  store_name?: string
  location?: string
  location_name?: string
  site?: string
}

export interface ItemClass extends BaseEntity {
  item_class_name: string
  description: string
  item_class_type: string
  asset_class?: string
  parent_item_class?: string
  default_uom?: string
  valuation_method?: string
  account?: string
  inventory_tracking?: boolean
  is_serialized?: boolean
  is_active?: boolean
}

export interface StockCountLine extends BaseEntity {
  stock_count: string
  inventory?: string
  item: string
  asset_tag?: string
  serial_nos?: string
  bin?: string
  zone?: string
  uom?: string
  snapshot_qty?: number
  counted_qty: number
  variance_qty?: number
  variance_value?: number
  variance_reason?: string
  is_reconciled?: boolean
}

export interface Organization extends BaseEntity {
  organization_name: string
  legal_name: string
  organizational_code?: string
  is_active?: boolean
}

export interface Note extends BaseEntity {
  title: string
  public?: boolean
  notify_on_login?: boolean
  notify_on_every_login?: boolean
  expire_notification_on?: string
  content?: string
}

export interface Holiday extends BaseEntity {
  holiday_name?: string
  holiday_date?: string
  applicable_to_labor_grp?: string
  specific_labor?: string
}

export interface NoteSeenBy extends BaseEntity {
  note?: string
  user?: string
}

export interface Contractor extends BaseEntity {
  contractor_name: string
}

export interface AnnualBudget extends BaseEntity {
  cost_code: string
  cost_code_name?: string
  year: number
  budgetary_amount: number
}

export interface LaborAvailabilityDetails extends BaseEntity {
  labor_availability?: string
  hour?: unknown
  status?: string
  reason?: string
}

export interface Trade extends BaseEntity {
  trade_name: string
  description: string
  on_staff?: boolean
  licensed?: boolean
  available_capacity?: number
}

export interface EmployeeSite extends BaseEntity {
  employee: string
  site: string
  department: string
  default?: boolean
}

export interface RequestActivityType extends BaseEntity {
  menu?: string
  type?: string
  state?: string
  role?: string
}

export interface LaborGroup extends BaseEntity {
  labor_group_name?: string
}

export interface LaborAvailability extends BaseEntity {
  labor?: string
  laborer?: string
  date?: string
}

export interface TradeAvailability extends BaseEntity {
  trade?: string
  specific_datetime?: string
  remaining_capacity?: number
  reserved_capacity?: number
  available_capacity?: number
}

export interface WorkScheduleDetails extends BaseEntity {
  work_schedule?: string
  day?: string
  start_time?: unknown
  end_time?: unknown
  is_working?: boolean
}

export interface LeaveType extends BaseEntity {
  leave_type_name?: string
}

export interface LeaveApplication extends BaseEntity {
  labor?: string
  leave_type?: string
  from_date?: string
  to_date?: string
  reason?: string
}

export interface CostCode extends BaseEntity {
  code: string
  description: string
  scope: string
  site?: string
  site_name?: string
}

export interface Account extends BaseEntity {
  account_code: string
  account_name: string
  account_type?: string
}

export interface TradeLabor extends BaseEntity {
  trade: string
  labor: string
  laborer?: string
  primary?: boolean
}

export interface Labor extends BaseEntity {
  labor_type: string
  labor_group?: string
  labor_group_name?: string
  employee?: string
  contractor?: string
  laborer?: string
  location?: string
  location_name?: string
  pr_line_no?: string
  labor_cost?: number
}

export interface WorkSchedule extends BaseEntity {
  schedule_name?: string
  applicable_to_labor_grp?: string
  specific_labor?: string
  start_date?: string
  end_date?: string
}

export interface TodoComment extends BaseEntity {
  todo_id?: string
  content?: string
  author?: string
}

export interface Todo extends BaseEntity {
  title?: string
  description?: string
  status?: string
  priority?: string
  due_date?: string
  completed?: boolean
}

export interface AssetPosition extends BaseEntity {
  position?: string
  position_name?: string
  asset?: string
  asset_name?: string
  date_installed?: string
  date_removed?: string
}

export interface AssetProperty extends BaseEntity {
  asset?: string
  asset_name?: string
  property?: string
  property_name?: string
  property_value?: string
  unit_of_measure?: string
  uom_short_name?: string
  property_type?: string
}

export interface Asset extends BaseEntity {
  workflow_state?: string
  asset_tag: string
  asset_class: string
  asset_class_name?: string
  description: string
  series?: string
  manufacturer?: string
  manufacturer_name?: string
  model?: string
  serial_number?: string
  date_purchased: string
  cost?: number
  block_number?: number
  manual?: unknown
  number_of_repairs?: number
  location: string
  site: string
  department: string
  assigned_to?: string
  inventory?: string
  system?: string
  position?: string
  item?: string
  defective?: boolean
  item_type?: string
  is_equipment?: boolean
  need_repair?: boolean
}

export interface LocationType extends BaseEntity {
  name?: string
}

export interface Disposed extends BaseEntity {
  asset: string
  condition?: string
  disposal_date: string
  disposal_reason: string
  disposal_method: string
  disposal_status?: string
  site: string
}

export interface Property extends BaseEntity {
  name: string
  description: string
  unit_of_measure: string
  unit_of_measure_name?: string
  property_type: string
  property_type_name?: string
  system?: boolean
  inactive?: boolean
}

export interface Location extends BaseEntity {
  name: string
  description?: string
  location_type?: string
  location_type_name?: string
  parent_location?: string
  site: string
  latitude?: number
  longitude?: number
  address: string
}

export interface Position extends BaseEntity {
  position_tag: string
  description: string
  attach_img?: unknown
  asset_class: string
  asset_class_name?: string
  system: string
  system_name?: string
  location?: string
  location_name?: string
  site?: string
  current_asset?: string
}

export interface Breakdown extends BaseEntity {
  equipment?: string
  breakdown_date?: string
  start_time?: string
  end_time?: string
  cause?: string
}

export interface EquipmentGroup extends BaseEntity {
  name?: string
}

export interface AssetClass extends BaseEntity {
  name: string
  description?: string
  due_date_lead_time?: number
  parent_asset_class?: string
  class_icon?: unknown
}

export interface IncidentEmployee extends BaseEntity {
  incident?: string
  employee?: string
  role_in_incident?: string
  injured?: boolean
  injury_severity?: string
  injury_description?: string
  ppe_used?: boolean
  treatment?: string
}

export interface SystemType extends BaseEntity {
  name?: string
}

export interface System extends BaseEntity {
  name: string
  description: string
  system_type?: string
  system_type_name?: string
  parent_system?: string
  location: string
  site: string
}

export interface AssetClassProperty extends BaseEntity {
  asset_class?: string
  asset_class_name?: string
  property?: string
  property_name?: string
  unit_of_measure?: string
  uom_short_name?: string
  default_value?: string
}

export interface PropertyType extends BaseEntity {
  name?: string
}

export interface AssetClassAvailability extends BaseEntity {
  asset_class?: string
  specific_datetime?: string
  remaining_capacity?: number
  reserved_capacity?: number
  available_capacity?: number
}

export interface PositionRelation extends BaseEntity {
  position_a?: string
  position_a_description?: string
  position_relation_type?: string
  position_b?: string
  position_b_description?: string
}

export interface Incident extends BaseEntity {
  title: string
  description: string
  incident_type: string
  incident_datetime: string
  date_reported: string
  location?: string
  asset?: string
  reported_by?: string
  site: string
  department?: string
  severity?: string
  immediate_action_taken?: string
  preventive_actions?: string
  assigned_to?: string
  closed_date?: string
}

export interface Equipment extends BaseEntity {
  equipment_type: string
  equipment_group?: string
  equipment_group_name?: string
  custodian?: string
  location?: string
  location_name?: string
  site: string
  inventory?: string
  pr_line_no?: string
  description?: string
  equipment_cost?: number
}

export interface WorkOrderChecklist extends BaseEntity {
  work_order_activity: string
  checklist: string
  inspector_id?: string
  inspector_name?: string
  inspection_date?: string
  remarks?: string
  status?: string
}

export interface WorkOrderEquipment extends BaseEntity {
  workflow_state?: string
  work_order_activity: string
  work_order_activity_desc?: string
  item: string
  item_name?: string
  equipment: string
  equipment_name?: string
  start_datetime: string
  end_datetime?: string
  total_hours_used?: number
  estimated_hours?: number
}

export interface WorkOrderLaborAssignment extends BaseEntity {
  workflow_state?: string
  work_order_labor?: string
  trade_id?: string
  start_datetime?: string
  end_datetime?: string
  lead?: boolean
  employee?: string
  hours_used?: number
}

export interface CategoryOfFailure extends BaseEntity {
  failure_name: string
  description?: string
  site: string
  active?: boolean
}

export interface WorkOrderActivity extends BaseEntity {
  workflow_state?: string
  work_order?: string
  work_order_name?: string
  description?: string
  work_item_type: string
  work_item?: string
  asset_name?: string
  activity_type?: string
  activity_type_name?: string
  position?: string
  assigned_to?: string
  does_it_need_repair?: boolean
  location: string
  site: string
  department: string
  start_date: string
  end_date?: string
}

export interface WorkOrderActivityLogs extends BaseEntity {
  work_order_activity: string
  work_order_activity_name?: string
  date: string
  log: string
}

export interface WorkOrderEquipmentAssignment extends BaseEntity {
  workflow_state?: string
  work_order_equipment?: string
  asset_class_id?: string
  start_datetime?: string
  end_datetime?: string
  equipment?: string
  hours_used?: number
}

export interface WorkOrder extends BaseEntity {
  workflow_state?: string
  work_order_type: string
  description: string
  category_of_failure?: string
  due_date: string
  priority?: string
  severity?: string
  incident?: string
  site: string
  department: string
  cost_code: string
}

export interface WorkOrderChecklistDetail extends BaseEntity {
  work_order_checklist?: string
  item_name?: string
  is_mandatory?: boolean
  remarks?: string
  status?: string
}

export interface WorkOrderEquipmentActualHours extends BaseEntity {
  wo_equip_id?: string
  date?: string
  hour?: string
  reason?: string
  comment?: string
  site?: string
  department?: string
  cost_code?: string
}

export interface WorkOrderParts extends BaseEntity {
  workflow_state?: string
  work_order_activity: string
  work_order_activity_desc?: string
  item: string
  item_name?: string
  unit_of_measure?: string
  total_actual_qty?: number
  total_avail_qty?: number
  date_required: string
  quantity_required: number
  quantity_issued?: number
  quantity_returned?: number
}

export interface WorkOrderLaborActualHours extends BaseEntity {
  wo_labor_id?: string
  date?: string
  time?: string
  reason?: string
  comment?: string
  site?: string
  department?: string
  cost_code?: string
}

export interface WorkOrderPartsReservation extends BaseEntity {
  work_order_parts?: string
  item_id?: string
  item?: string
  unit_of_measure?: string
  inventory?: string
  avail_quantity_data?: string
  date_reserved?: string
  quantity_reserved?: number
  status?: string
}

export interface WorkOrderLabor extends BaseEntity {
  workflow_state?: string
  work_order_activity: string
  work_order_activity_desc?: string
  trade: string
  trade_name?: string
  labor: string
  laborer?: string
  lead?: boolean
  start_datetime: string
  end_datetime?: string
  total_hours_used?: number
  estimated_hours?: number
}

export interface MaintenanceOrder extends BaseEntity {
  created_date?: string
  work_order?: string
}

export interface ChecklistDetails extends BaseEntity {
  checklist: string
  item_name?: string
  is_mandatory?: boolean
}

export interface MaintenanceEquipment extends BaseEntity {
  maintenance_activity?: string
  equipment?: string
  required_qty?: number
  required_hours?: number
}

export interface SensorData extends BaseEntity {
  sensor?: string
  value?: string
  timestamp?: string
}

export interface MaintenanceTrade extends BaseEntity {
  maintenance_activity?: string
  trade?: string
  required_qty?: number
  required_hours?: number
}

export interface MaintenanceCondition extends BaseEntity {
  planned_maintenance_activity?: string
  maintenance_plan?: string
  maintenance_activity?: string
  sensor?: string
  uom_short_name?: string
  property_type?: string
  comparison_operator?: string
  threshold_property?: string
}

export interface MaintenanceOrderDetail extends BaseEntity {
  maintenance_order?: string
  seq_num?: number
  maint_req?: string
  asset?: string
  due_date?: string
  resource_availability_status?: string
}

export interface MaintenancePlan extends BaseEntity {
  description?: string
  asset_class?: string
  asset_class_name?: string
  manufacturer?: string
  manufacturer_name?: string
  model?: string
  model_name?: string
}

export interface PlannedMaintenanceActivity extends BaseEntity {
  maintenance_plan?: string
  maintenance_plan_name?: string
  maintenance_activity?: string
  maintenance_activity_name?: string
  checklist?: string
  checklist_name?: string
  maintenance_schedule?: string
  maintenance_type?: string
}

export interface MaintenanceCalendar extends BaseEntity {
  planned_maintenance_activity?: string
  maintenance_plan?: string
  maintenance_activity?: string
  frequency?: string
  lead_calendar_days?: number
  last_maintenance_date_property?: string
}

export interface Sensor extends BaseEntity {
  sensor_name?: string
  asset?: string
  asset_name?: string
  asset_property?: string
  uom_short_name?: string
  property_type?: string
  root_topic_name?: string
  collection_frequency?: string
  site?: string
}

export interface MaintenanceParts extends BaseEntity {
  maintenance_activity?: string
  item?: string
  quantity?: number
}

export interface MaintenanceActivity extends BaseEntity {
  activity_name: string
  description?: string
}

export interface MaintenanceInterval extends BaseEntity {
  planned_maintenance_activity?: string
  maintenance_plan?: string
  maintenance_activity?: string
  lead_interval?: number
  interval?: number
  interval_unit_of_measure?: string
  running_interval_property?: string
  last_interval_property?: string
}

export interface MaintenanceRequest extends BaseEntity {
  workflow_state?: string
  requestor?: string
  requested_date?: string
  description?: string
  priority?: string
  request_type?: string
  asset?: string
  location?: string
  site?: string
  department?: string
  position?: string
  incident?: string
  planned_maintenance_activity?: string
  due_date?: string
  next_maintenance_request?: string
  closed_date?: string
  work_order_activity?: string
  property?: string
  maintenance_interval_property?: string
  running_interval_value?: number
}

export interface Checklist extends BaseEntity {
  checklist_name: string
  checklist_type?: string
}
