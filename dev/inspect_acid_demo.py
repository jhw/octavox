from rv.api import read_sunvox_file

if __name__=="__main__":
    project=read_sunvox_file("dev/acid-demo.sunvox")
    modules={module.name:module for module in project.modules}
    mm=modules["acid bass"]
    for mod in mm.project.modules:
        print (mod)
