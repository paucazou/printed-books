#!/usr/bin/python3

import functools as fc
import json
import os
import time

languages={
        'eng':"Anglais",
        'fra':"Français",
        "lat":"Latin",
        "heb":"Hébreu",
        '':"PROBLEM\n\n\n"
        }


def accumulate(l):
    return fc.reduce(lambda x,y: x+y, l)

def crawl(data) -> str:
    """Main function that crawls the
    data to return a HTML table as a string"""
    table='''
<table class="table table-hover">
    <thead>
        <tr class="table-dark">
            <th scope="col" >Titre</th>
            <th scope="col" >Auteur</th>
            <th scope="col" >Format</th>
            <th scope="col" >Langue</th>
            <th scope="col" >Prix (€)</th>
            <th scope="col" >Pages</th>
        </tr>
    </thead>
    <tbody>'''
    for item in data:
        table += _crawl(item,0)["table"]

    table += "</tbody></table>"
    return table

def _sort_data(data):
    def sort_key(x):
        return x['title']

    def sort(items):
        if 'data' in items:
            items['data'] = sorted(
                    (sort(elt) for elt in items['data']),
                    key = sort_key)
        return items
    return sorted(
            (sort(elt) for elt in data),
            key = sort_key)
        
def _title(title,lvl) -> str:
    """Return the title with non secable space padding matching with lvl"""
    padding=4
    return title.rjust(len(title) + padding * lvl,' ')

def _crawl(item, lvl) -> dict:
    """Recursive function
    The return value contains the text with one or more rows of <tr>
    lvl is the deepness of data
    """
    columns=""
    if "data" in item:
        line='<tr class="table-info">{}</tr>\n'
        lines=[ _crawl(x,lvl+1) for x in item["data"] ]
        price=round(accumulate([l["price"] for l in lines]), 2)
        pages=accumulate([l["pages"] for l in lines])
        tit=_title(item["title"],lvl)
        for k in tit, item["author"], "/", "/", price, pages:
            columns += f"<td>{k}</td>\n"
        columns=line.format(columns)

        for l in lines:
            columns += l["table"]
    else:
        # last level
        line="<tr class='table-light'>{}</tr>\n"
        for k in "title author book_size language price page_count".split():
            if k == "language":
                columns += f"<td>{languages[item[k]]}</td>\n"
                continue
            elif k == "title":
                columns +=f"<td>{_title(item[k],lvl)}</td>\n"
                continue
            columns += f"<td>{item[k]}</td>\n"
        price=item["price"]
        pages=item["page_count"]
        columns=line.format(columns)

    return {
            "table":columns,
            "price":price,
            "pages":pages,
            }

def gen_page():
    with open("data.txt") as f:
        data=_sort_data(json.loads(f.read()))
    with open("table.html") as f:
        page=f.read()
    table = crawl(data)
    # Last modif
    t=os.path.getmtime("data.txt")
    time_to_print=time.strftime("%d/%m/%Y", time.localtime(t))

    page=page.format(table=table, modif_time=time_to_print)
    with open("out.html",'w') as f:
        f.write(page)

if __name__ == '__main__':
    gen_page()

