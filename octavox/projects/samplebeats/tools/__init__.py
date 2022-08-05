import yaml

Profiles=yaml.safe_load("""
default:
  kk: 0.7
  sn: 0.7
  oh: 0.4
  ch: 0.4
strict:
  kk: 1.0
  sn: 1.0
  oh: 0.8
  ch: 0.8
wild:
  kk: 0.4
  sn: 0.4
  oh: 0.2
  ch: 0.2
""")

if __name__=="__main__":
    pass
