def to_file_name(name: str):
    name = name.lower().replace(' ', '_')
    return ''.join([c if c.isalpha() else '_' for c in name])


def as_camel_case(name: str):
    name = to_file_name(name)
    return ''.join([c.capitalize() for c in name.split('_')])
