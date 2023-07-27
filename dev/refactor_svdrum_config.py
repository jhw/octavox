import yaml

if __name__=="__main__":
    struct=yaml.safe_load(open("octavox/projects/picobeats/svdrum.yaml").read())
    for key in struct:
        struct[key]=[{"mod": item[0],
                      "id": item[1]}
                     for item in struct[key]]
    with open("tmp/svdrum.yaml", 'w') as f:
        f.write(yaml.safe_dump(struct,
                               default_flow_style=False))
