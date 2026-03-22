import json, os, glob

base = '/Users/macbookair/dev_projects/enhanced-ueml/system-generation/eam-fast-api/backend/app/modules'
out_dir = '/Users/macbookair/dev_projects/enhanced-ueml/system-generation/eam-fast-api/docs/gaps/_scripts'
files = sorted(glob.glob(os.path.join(base, '*/entities/*.json')))

graph = {}

for f in files:
    with open(f) as fh:
        data = json.load(fh)
    name = data.get('name', os.path.basename(f).replace('.json',''))
    module = f.split('/modules/')[1].split('/')[0]
    fields = data.get('fields', [])
    links_config = data.get('links', [])
    children_config = data.get('children', [])
    
    link_fields = []
    all_fields = []
    for field in fields:
        fn = field.get('name','')
        ft = field.get('field_type','')
        le = field.get('link_entity','')
        ro = field.get('readonly', False)
        req = field.get('required', False)
        all_fields.append({
            'name': fn, 'type': ft, 'link': le, 'readonly': ro, 'required': req
        })
        if le:
            link_fields.append({
                'field': fn, 'target': le, 'readonly': ro, 'required': req
            })
    
    # Entities that show this entity as a related tab
    related_from = [l.get('entity','') for l in links_config]
    
    graph[name] = {
        'module': module,
        'field_count': len(fields),
        'links': link_fields,
        'fields': all_fields,
        'related_tabs': related_from,
        'children': children_config,
    }

# 1. Find which entities are referenced by OTHER entities (as link targets)
referenced_as_target = set()
for name, info in graph.items():
    for link in info['links']:
        if link['target'] in graph:
            referenced_as_target.add(link['target'])
    for tab in info['related_tabs']:
        if tab in graph:
            referenced_as_target.add(tab)

# 2. Find unreferenced entities (no other entity links to them or shows them as tab)
unreferenced = []
for name in sorted(graph.keys()):
    # Check if ANY other entity references this one
    is_referenced = False
    for other_name, other_info in graph.items():
        if other_name == name:
            continue
        for link in other_info['links']:
            if link['target'] == name:
                is_referenced = True
                break
        if is_referenced:
            break
        for tab in other_info['related_tabs']:
            if tab == name:
                is_referenced = True
                break
        if is_referenced:
            break
    if not is_referenced:
        unreferenced.append((name, graph[name]['module']))

with open(os.path.join(out_dir, 'unreferenced_entities.txt'), 'w') as f:
    f.write("ENTITIES NOT REFERENCED BY ANY OTHER ENTITY\n")
    f.write("=" * 60 + "\n\n")
    for name, module in unreferenced:
        f.write(f"  {name} ({module})\n")
    f.write(f"\nTotal: {len(unreferenced)}\n")

# 3. Build per-module dependency lists for each entity
# For each entity, what does it DEPEND on (non-readonly links to other entities)
with open(os.path.join(out_dir, 'dependency_list.txt'), 'w') as f:
    for module in ['core_eam', 'asset_management', 'maintenance_mgmt', 'purchasing_stores', 'work_mgmt']:
        f.write(f"\n{'='*60}\n")
        f.write(f"MODULE: {module}\n")
        f.write(f"{'='*60}\n\n")
        for name in sorted(graph.keys()):
            if graph[name]['module'] != module:
                continue
            deps = []
            for link in graph[name]['links']:
                target = link['target']
                if target == name:  # self-reference
                    deps.append(f"self ({link['field']})")
                elif target in ('users', 'workflow_states'):
                    deps.append(f"{target} (system)")
                else:
                    ro_tag = ' [ro]' if link['readonly'] else ''
                    deps.append(f"{target}{ro_tag}")
            dep_str = ', '.join(deps) if deps else '— (standalone)'
            f.write(f"{name}: {dep_str}\n")

# 4. Find which entities reference entities from OTHER modules (cross-module deps)
with open(os.path.join(out_dir, 'cross_module_deps.txt'), 'w') as f:
    f.write("CROSS-MODULE DEPENDENCIES\n")
    f.write("=" * 60 + "\n\n")
    for name in sorted(graph.keys()):
        info = graph[name]
        for link in info['links']:
            target = link['target']
            if target in graph and graph[target]['module'] != info['module']:
                f.write(f"{name} ({info['module']}) -> {target} ({graph[target]['module']})\n")

print("Done. Written:")
print("  unreferenced_entities.txt")
print("  dependency_list.txt")
print("  cross_module_deps.txt")
