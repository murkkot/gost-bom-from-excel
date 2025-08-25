import re

# Process designator sequences according to GOST
def process_designator_sequence(designators):
    if len(designators) == 1:
        return designators[0]
    
    # Parse all designators into (prefix, number) tuples
    parsed = []
    for d in designators:
        match = re.match(r'([^\d]*)(\d+)', d)
        if match:
            prefix, num = match.groups()
            parsed.append((prefix, int(num)))
        else:
            return ',  '.join(designators)
    
    # Group into consecutive sequences
    groups = []
    current_group = [designators[0]]
    
    for i in range(1, len(designators)):
        prev_prefix, prev_num = parsed[i-1]
        curr_prefix, curr_num = parsed[i]
        
        if (curr_prefix == prev_prefix) and (curr_num == prev_num + 1):
            current_group.append(designators[i])
        else:
            groups.append(current_group)
            current_group = [designators[i]]
    
    groups.append(current_group)
    
    # Format each group appropriately
    formatted_groups = []
    for group in groups:
        if len(group) >= 3:
            formatted_groups.append(f"{group[0]}...{group[-1]}")
        else:
            formatted_groups.append(",".join(group))
    
    return ",".join(formatted_groups)