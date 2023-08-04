### Octavox

Octavox is a project to generate and mutate interesting looking Sunvox sample chains, for slicing and performing in a hardware system like Elektron's Octatrack or Digitakt

https://www.elektron.se/en/octratrack-mkii-explorer

https://www.elektron.se/en/digitakt-explorer

This project makes heavy use of Sunvox and Radiant Voices, to whose authors `@nightradio` and  `@gldnspd` I am deeply indebted

https://www.warmplace.ru/soft/sunvox/

https://github.com/metrasynth/radiant-voices

### Installation

```
jhw@Justins-Air octavox % . ./setenv.sh 
jhw@Justins-Air octavox % python -m venv env
jhw@Justins-Air octavox % . env/bin/activate
(env) jhw@Justins-Air octavox % pip install --upgrade pip
Requirement already satisfied: pip in ./env/lib/python3.8/site-packages (22.1.2)
Collecting pip
  Using cached pip-23.1.2-py3-none-any.whl (2.1 MB)
Installing collected packages: pip
  Attempting uninstall: pip
    Found existing installation: pip 22.1.2
    Uninstalling pip-22.1.2:
      Successfully uninstalled pip-22.1.2
Successfully installed pip-23.1.2
(env) jhw@Justins-Air octavox % pip install -r requirements.txt 
Collecting git+https://github.com//metrasynth/radiant-voices (from -r requirements.txt (line 1))
  Cloning https://github.com//metrasynth/radiant-voices to /private/var/folders/ms/y9_pfxl16qj49c9qxg8dy76r0000gn/T/pip-req-build-pwcp8z0_
  Running command git clone --filter=blob:none --quiet https://github.com//metrasynth/radiant-voices /private/var/folders/ms/y9_pfxl16qj49c9qxg8dy76r0000gn/T/pip-req-build-pwcp8z0_
  Resolved https://github.com//metrasynth/radiant-voices to commit 13db34eb0c451748401abc8e887f3229c968fe37
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Requirement already satisfied: lxml in ./env/lib/python3.8/site-packages (from -r requirements.txt (line 2)) (4.9.1)
Requirement already satisfied: numpy in ./env/lib/python3.8/site-packages (from -r requirements.txt (line 3)) (1.21.4)
Requirement already satisfied: pyyaml in ./env/lib/python3.8/site-packages (from -r requirements.txt (line 4)) (5.4.1)
Requirement already satisfied: attrs>=19.3.0 in ./env/lib/python3.8/site-packages (from radiant-voices==1.0.3->-r requirements.txt (line 1)) (21.2.0)
Requirement already satisfied: python-slugify in ./env/lib/python3.8/site-packages (from radiant-voices==1.0.3->-r requirements.txt (line 1)) (5.0.2)
Requirement already satisfied: hexdump in ./env/lib/python3.8/site-packages (from radiant-voices==1.0.3->-r requirements.txt (line 1)) (3.3)
Requirement already satisfied: logutils in ./env/lib/python3.8/site-packages (from radiant-voices==1.0.3->-r requirements.txt (line 1)) (0.3.5)
Requirement already satisfied: networkx in ./env/lib/python3.8/site-packages (from radiant-voices==1.0.3->-r requirements.txt (line 1)) (2.6.3)
Requirement already satisfied: text-unidecode>=1.3 in ./env/lib/python3.8/site-packages (from python-slugify->radiant-voices==1.0.3->-r requirements.txt (line 1)) (1.3)
```

