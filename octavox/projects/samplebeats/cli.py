import cmd, sys

class SamplebeatsShell(cmd.Cmd):

    intro="Welcome to Octavox Samplebeats :)"
    prompt=">>> "
    
    def do_hello(self, arg):
        print ("hello")
    
    def do_exit(self, arg):
        return self.do_quit(arg)
    
    def do_quit(self, arg):
        print ("exiting")
        return True

if __name__=="__main__":
    SamplebeatsShell().cmdloop()
