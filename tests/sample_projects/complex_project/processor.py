def process(records, primary, secondary, tertiary, quaternary, quinary, senary, septenary):
    results = []
    for record in records:
        if record:
            if primary:
                if secondary:
                    if tertiary:
                        results.append(record)
        elif quaternary:
            results.append(quinary or senary or septenary)
    return results

