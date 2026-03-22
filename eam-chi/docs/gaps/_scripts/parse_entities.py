import json, os, glob

base = '/Users/macbookair/dev_projects/enhanced-ueml/system-generation/eam-fast-api/backend/app/modules'
files = sorted(glob.glob(os.path.join(base, '*/entities/*.json')))

results = []
for f in files:
    with open(f) as fh:
        data = json.load(fh)
    name = data.get('name', os.path.basename(f).replace('.json',''))
    module = f.split('/modules/')[1].split('/')[0]
    fields = data.get('fields', [])
    link_fields = []
    for field in fields:
        le = field.get('link_entity','')
        if le:
            link_fields.append({
                'field': field.get('name',''),
                'target': le,
                'readonly': field.get('readonly', False),
                'required': field.get('required', False),
            })
    results.append({
        'name': name,
        'module': module,
        'field_count': len(fields),
        'links': link_fields
    })

for r in results:
    link_str = ', '.join([
        f"{l['field']}->{l['target']}{'(ro)' if l['readonly'] else ''}{'(req)' if l['required'] else ''}"
        for l in r['links']
    ])
    print(f"{r['name']}|{r['module']}|{r['field_count']}|{link_str}")
