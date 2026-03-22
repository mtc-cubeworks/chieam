#!/usr/bin/env python3
"""Fix collapsed sidebar navigation in default.vue"""

filepath = '/home/cwadmin/eam-tests/eam-spmc/frontend/app/layouts/default.vue'

with open(filepath, 'r') as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]

    # Add :popover="true" after :tooltip="true"
    if ':tooltip="true"' in line and ':popover' not in line:
        new_lines.append(line)
        # Get the indentation from the tooltip line
        indent = line[:len(line) - len(line.lstrip())]
        new_lines.append(f'{indent}:popover="true"\n')
        i += 1
        continue

    # Remove the link: 'overflow-hidden' line
    if "link: 'overflow-hidden'," in line:
        i += 1
        continue

    # Fix the item line - remove broken data-[collapsed=true]: selectors
    if "item: 'data-[collapsed=true]:justify-center" in line:
        indent = line[:len(line) - len(line.lstrip())]
        new_lines.append(f"{indent}item: 'transition-all duration-300',\n")
        i += 1
        continue

    new_lines.append(line)
    i += 1

with open(filepath, 'w') as f:
    f.writelines(new_lines)

print('Fix applied successfully')
print('Changes:')
print('  1. Added :popover="true" to UNavigationMenu')
print('  2. Removed link: overflow-hidden from ui prop')
print('  3. Simplified item classes (removed broken data-[collapsed] selectors)')
