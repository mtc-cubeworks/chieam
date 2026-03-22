import json, os, glob

base = '/Users/macbookair/dev_projects/enhanced-ueml/system-generation/eam-fast-api/backend/app/modules'
out_dir = '/Users/macbookair/dev_projects/enhanced-ueml/system-generation/eam-fast-api/docs/gaps/_scripts'
files = sorted(glob.glob(os.path.join(base, '*/entities/*.json')))

output_lines = []
# Build full graph: entity -> list of (field_name, target_entity, readonly, required)
graph = {}
all_entities = set()

for f in files:
    with open(f) as fh:
        data = json.load(fh)
    name = data.get('name', os.path.basename(f).replace('.json',''))
    module = f.split('/modules/')[1].split('/')[0]
    fields = data.get('fields', [])
    all_entities.add(name)
    link_fields = []
    all_field_info = []
    for field in fields:
        fn = field.get('name','')
        ft = field.get('field_type','')
        le = field.get('link_entity','')
        ro = field.get('readonly', False)
        req = field.get('required', False)
        all_field_info.append({
            'name': fn, 'type': ft, 'link': le, 'readonly': ro, 'required': req
        })
        if le:
            link_fields.append({
                'field': fn, 'target': le, 'readonly': ro, 'required': req
            })
    graph[name] = {
        'module': module,
        'field_count': len(fields),
        'links': link_fields,
        'fields': all_field_info
    }

# 1. Write full entity map
with open(os.path.join(out_dir, 'entity_map.txt'), 'w') as f:
    for name in sorted(graph.keys()):
        info = graph[name]
        f.write(f"\n=== {name} ({info['module']}) — {info['field_count']} fields ===\n")
        for fi in info['fields']:
            suffix = ''
            if fi['link']: suffix += f" -> {fi['link']}"
            if fi['readonly']: suffix += ' [ro]'
            if fi['required']: suffix += ' [req]'
            f.write(f"  {fi['name']} ({fi['type']}){suffix}\n")
        if info['links']:
            f.write(f"  LINKS: {', '.join(l['field']+'->'+l['target'] for l in info['links'])}\n")

# 2. Find circular references (A->B and B->A)
circular = []
for name, info in graph.items():
    for link in info['links']:
        target = link['target']
        if target in graph:
            for back_link in graph[target]['links']:
                if back_link['target'] == name:
                    pair = tuple(sorted([name, target]))
                    if pair not in [(c[0], c[1]) for c in circular]:
                        circular.append((pair[0], pair[1], 
                            f"{name}.{link['field']}->{target}", 
                            f"{target}.{back_link['field']}->{name}"))

with open(os.path.join(out_dir, 'circular_refs.txt'), 'w') as f:
    f.write("CIRCULAR REFERENCES (A->B and B->A)\n")
    f.write("="*60 + "\n\n")
    for a, b, fwd, bck in sorted(circular):
        f.write(f"{a} <-> {b}\n")
        f.write(f"  Forward: {fwd}\n")
        f.write(f"  Back:    {bck}\n\n")

# 3. Find redundant site/department/cost_code on child entities
# (child = entity with a parent link like purchase_request_line -> purchase_request)
redundancies = []
parent_child_map = {}
for name, info in graph.items():
    for link in info['links']:
        # Heuristic: if field name matches a known parent pattern
        target = link['target']
        # Check if target entity already has site/dept/cost_code
        if target in graph:
            target_fields = {l['field']: l['target'] for l in graph[target]['links']}
            current_fields = {l['field']: l['target'] for l in info['links']}
            # If both have site, dept, cost_code and one is a child
            for redundant_field in ['site', 'department', 'cost_code']:
                if redundant_field in current_fields and redundant_field in target_fields:
                    if current_fields[redundant_field] == target_fields[redundant_field]:
                        # This entity links to target, and both have the same redundant field
                        redundancies.append((name, target, link['field'], redundant_field))

with open(os.path.join(out_dir, 'redundancies.txt'), 'w') as f:
    f.write("POTENTIAL REDUNDANT FIELDS (child has same link as parent)\n")
    f.write("="*60 + "\n\n")
    seen = set()
    for child, parent, parent_field, redundant in sorted(redundancies):
        key = (child, parent, redundant)
        if key not in seen:
            seen.add(key)
            f.write(f"{child}.{redundant} — also on {parent} (linked via {parent_field})\n")

# 4. Entities that link to non-existent entities
broken = []
for name, info in graph.items():
    for link in info['links']:
        if link['target'] not in graph and link['target'] != 'users' and link['target'] != 'workflow_states':
            broken.append((name, link['field'], link['target']))

with open(os.path.join(out_dir, 'broken_links.txt'), 'w') as f:
    f.write("BROKEN LINKS (target entity not found)\n")
    f.write("="*60 + "\n\n")
    for name, field, target in sorted(broken):
        f.write(f"{name}.{field} -> {target} (NOT FOUND)\n")

# 5. Dependency order analysis based on masterfile sheet order
masterfile_order = [
    'organization', 'site', 'department', 'location_type', 'location',
    'system_type', 'system', 'unit_of_measure', 'property', 'manufacturer',
    'model', 'vendor', 'asset_class', 'asset_class_property', 'item',
    'position', 'position_relation', 'asset', 'asset_property', 'asset_position'
]

# Check if any entity in masterfile_order links to something that comes AFTER it
order_violations = []
for i, entity in enumerate(masterfile_order):
    if entity in graph:
        for link in graph[entity]['links']:
            target = link['target']
            if target in masterfile_order:
                target_idx = masterfile_order.index(target)
                if target_idx > i and not link['readonly']:
                    order_violations.append((entity, link['field'], target, i, target_idx))

with open(os.path.join(out_dir, 'order_violations.txt'), 'w') as f:
    f.write("MASTERFILE ORDER VIOLATIONS\n")
    f.write("(Entity links to something that should be created AFTER it)\n")
    f.write("="*60 + "\n\n")
    for ent, field, target, ei, ti in order_violations:
        f.write(f"#{ei+1} {ent}.{field} -> #{ti+1} {target} (links forward in creation order)\n")

print("Done. Files written to:", out_dir)
print(f"  entity_map.txt")
print(f"  circular_refs.txt")
print(f"  redundancies.txt")
print(f"  broken_links.txt")
print(f"  order_violations.txt")
