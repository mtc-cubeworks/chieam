# Entity Creation Order

All 113 entities in dependency order. Create from top to bottom.

---

## Tier 1 — Standalone (no dependencies)

1. organization
2. account
3. currency
4. unit_of_measure
5. location_type
6. system_type
7. property_type
8. equipment_group
9. labor_group
10. leave_type
11. contractor
12. manufacturer
13. request_activity_type
14. note
15. error_log
16. checklist
17. maintenance_activity
18. category_of_failure
19. reason_code

## Tier 2 — Depends on Tier 1 only

20. site (→ organization)
21. model (→ manufacturer)
22. trade (standalone, but grouped here with labor ecosystem)
23. property (→ unit_of_measure, property_type)
24. item_class (→ unit_of_measure, account; self-ref for parent)
25. checklist_details (→ checklist)
26. note_seen_by (→ note)

## Tier 3 — Depends on Tier 1–2

27. department (→ site, account, cost_code)
28. cost_code (→ site)
29. location (→ location_type, site; self-ref for parent)
30. vendor (→ ~~site~~; standalone after fix)
31. employee (→ users)
32. asset_class (self-ref for parent)
33. maintenance_plan (→ asset_class, manufacturer, model)
34. trade_availability (→ trade)

## Tier 4 — Depends on Tier 1–3

35. employee_site (→ employee, site, department)
36. labor (→ labor_group, employee, contractor, location)
37. system (→ system_type, location; self-ref for parent)
38. store (→ location)
39. asset_class_property (→ asset_class, property, unit_of_measure)
40. asset_class_availability (→ asset_class)
41. item (→ item_class, account, vendor, asset_class, unit_of_measure)
42. annual_budget (→ cost_code)
43. planned_maintenance_activity (→ maintenance_plan, maintenance_activity, checklist, request_activity_type)
44. maintenance_trade (→ maintenance_activity, trade)
45. maintenance_parts (→ maintenance_activity, item)

## Tier 5 — Depends on Tier 1–4

46. trade_labor (→ trade, labor)
47. labor_availability (→ labor)
48. work_schedule (→ labor_group, labor)
49. holiday (→ labor_group, labor)
50. leave_application (→ labor, leave_type)
51. zone (→ store)
52. bin (→ store)
53. position (→ asset_class, system, location)
54. maintenance_calendar (→ planned_maintenance_activity, property)
55. maintenance_interval (→ planned_maintenance_activity, unit_of_measure, property)
56. maintenance_equipment (→ maintenance_activity, equipment_group)

## Tier 6 — Depends on Tier 1–5

57. labor_availability_details (→ labor_availability)
58. work_schedule_details (→ work_schedule)
59. position_relation (→ position)
60. inventory (→ item, site, location, store, zone, bin, employee, asset)
61. asset (→ asset_class, location, site, department, system, position, item, employee)
62. maintenance_condition (→ planned_maintenance_activity, sensor, property)

## Tier 7 — Depends on Tier 1–6

63. asset_property (→ asset, property, unit_of_measure)
64. asset_position (→ position, asset)
65. sub_asset (→ asset)
66. disposed (→ asset)
67. equipment (→ equipment_group, employee, location, inventory)
68. sensor (→ asset, asset_property)
69. sensor_data (→ sensor)
70. incident (→ location, asset, site, department, employee)
71. stock_ledger_entry (→ item, store, bin, site)

## Tier 8 — Transactions (Work Orders)

72. work_order (→ category_of_failure, incident, site, department, cost_code)
73. work_order_activity (→ work_order, asset, position, labor, location, site, department)
74. work_order_activity_logs (→ work_order_activity)
75. work_order_labor (→ work_order_activity, trade, labor)
76. work_order_equipment (→ work_order_activity, item, equipment)
77. work_order_parts (→ work_order_activity, item, unit_of_measure)
78. work_order_checklist (→ work_order_activity, checklist, employee)
79. work_order_checklist_detail (→ work_order_checklist)
80. work_order_labor_assignment (→ work_order_labor, labor)
81. work_order_labor_actual_hours (→ work_order_labor)
82. work_order_equipment_assignment (→ work_order_equipment, equipment)
83. work_order_equipment_actual_hours (→ work_order_equipment)
84. work_order_parts_reservation (→ work_order_parts, unit_of_measure, inventory)

## Tier 9 — Transactions (Maintenance)

85. maintenance_request (→ employee, asset, location, site, department, position, incident, planned_maintenance_activity, maintenance_interval, work_order_activity, property)
86. maintenance_order (→ work_order)
87. maintenance_order_detail (→ maintenance_order, maintenance_request, asset)
88. service_request (→ asset, site, location, work_order, incident)
89. incident_employee (→ incident, employee)
90. breakdown (→ equipment)

## Tier 10 — Transactions (Purchasing)

91. purchase_request (→ employee, work_order_activity, maintenance_request, site, department, cost_code)
92. purchase_request_line (→ purchase_request, item, unit_of_measure, currency, account, cost_code, vendor)
93. request_for_quotation (→ purchase_request, employee, vendor)
94. rfq_line (→ request_for_quotation, purchase_request_line, item)
95. purchase_order (→ vendor, site, department, cost_code)
96. purchase_order_line (→ purchase_order, purchase_request_line, item)
97. purchase_receipt (→ purchase_order_line, item, location, account)
98. purchase_return (→ inventory, item, unit_of_measure, site, department, cost_code)
99. sales_order (→ currency, site)
100. sales_order_item (→ sales_order, item, unit_of_measure)

## Tier 11 — Transactions (Stores / Inventory)

101. item_issue (→ employee, work_order_activity, site, department, cost_code)
102. item_issue_line (→ item_issue, work_order_parts, work_order_equipment, inventory, store, bin, zone)
103. item_return (→ employee, work_order_activity, site, department, cost_code)
104. item_return_line (→ item_return, work_order_parts, work_order_equipment, item)
105. transfer (→ employee, work_order_activity, inventory, labor, equipment, purchase_request_line, site, location, store, bin, zone, vendor)
106. transfer_receipt (→ transfer, inventory, unit_of_measure, location, site)
107. putaway (→ transfer, item_return_line, asset, item, site, store, bin, zone)
108. stock_count (→ store, site)
109. stock_count_line (→ stock_count, inventory, item, bin, zone, unit_of_measure, reason_code)
110. stock_count_task (→ stock_count, bin)
111. inventory_adjustment (→ stock_count, location, store, site, account)
112. inventory_adjustment_line (→ inventory_adjustment, inventory, item, bin, zone, unit_of_measure, account)
113. inspection (→ employee, site, inventory)
