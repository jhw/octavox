import yaml

if __name__=="__main__":
    struct=yaml.safe_load(open("octavox/projects/slicebeats/curated.yaml").read())
    modstruct={k: "|".join(["(%s)" % v for v in V])
               for k, V in struct.items()}
    with open("tmp/curated.yaml", 'w') as f:
        f.write(yaml.safe_dump(modstruct,
                               default_flow_style=False))
