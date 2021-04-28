#!/usr/bin/env python3

import os
import shlex
import pathlib
from subprocess import check_output
from collections import defaultdict

pages = defaultdict(list)

for dirpath, dirnames, filenames in os.walk("packages"):
    path_components = dirpath.split("/")[1:]

    if path_components == []:
        continue

    if "doc" in path_components:
        path_components.remove("doc")

    module_key = os.path.join(*path_components)
    path_components = ["antora", "modules"] + path_components + ["pages"]

    for fname in (f for f in filenames if f.endswith(".md")):
        fpath = os.path.join(dirpath, fname)
        new_name = fname.split(".")[0]

        if new_name == "README":
            new_name = "index"

        pages[module_key].append(new_name)

        new_name = new_name + ".adoc"
        new_path = os.path.join(*path_components, new_name)

        p = pathlib.Path(new_path)
        p.parent.mkdir(parents=True, exist_ok=True)

        pandoc = "pandoc --wrap=none --reference-links -t asciidoc -f gfm -o %s %s"
        check_output(shlex.split(pandoc % (os.path.abspath(new_path), os.path.abspath(fpath))))

for module_key, pages in pages.items():
    page_path = os.path.join(*os.path.split(module_key)[1:])
    with open(os.path.join("antora/modules", module_key, "nav.adoc"), "w") as fp:
        for page in pages:
            if page == "index":
                fp.write("* xref:%s:index.adoc[%s]\n" % (module_key, module_key))
            else:
                fp.write("** xref:%s:%s.adoc[%s]\n" % (module_key, page, page))
