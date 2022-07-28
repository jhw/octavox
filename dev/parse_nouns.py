import lxml.html as html

import yaml

if __name__=="__main__":
    doc=html.fromstring(open("dev/nouns.html").read())
    terms=[]
    for link in doc.xpath("//a"):
        if not ("href" in link.attrib and
                link.attrib["href"].startswith("/how-to-use")):
            continue
        text=link.text
        if len(text) < 3:
            continue
        tokens=text.split(" ")
        if len(tokens) > 1:
            continue        
        terms.append(text)
    with open("tmp/nouns.yaml", 'w') as f:
        f.write(yaml.safe_dump(sorted(terms)))
