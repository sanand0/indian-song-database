from sqlobject import *
import film, trans, cgi, cgitb

cgitb.enable()
film.connect()

print "Content-Type: text/html"     # HTML is following
print                               # blank line, end of headers

def show(e, related=0):
    out = e.type + " <a href='?id=" + str(e.id) + "'>" + e.name + "</a> (" + e.db + ", " + e.lang + ")"
    if related:
        count = 3
        for r in film.relations(e):
            out = out + ", " + r[0] + " <a href='?id=" + str(r[1].id) + "'>" + r[1].name + "</a>"
            count = count - 1
            if count <= 0: break
    return out

def show_id(ids):
    for id in form.getlist("id"):
        entity = film.Entity.get(id)
        if entity:
            ids = list(film.identicals(entity))
            for id in ids:
                print "<h1>", show(id), "</h1>"
                for rel in film.relations(id):
                    print "<li>", rel[0], show(rel[1], 1)

def show_search(queries):
    print "<form action='' method='GET'><input type='hidden' name='link' value='1'>"
    for q in queries:
        for entity in film.Entity.select(OR(film.Entity.q.name==q, film.Entity.q.tran==trans.trans(q)), orderBy=(film.Entity.q.type,film.Entity.q.name)):
            print '<br><input type="checkbox" name="' + str(entity.id) + '">', show(entity, 1)
    print "<br><input type='submit' value='Make identical'></form>"

def link(form):
    entities = list(film.Entity.get(key) for key in form if key.isdigit())
    film.identical(entities)
    print '<h1>Made identical</h1>', '<br>'.join((show(e) for e in entities))

form = cgi.FieldStorage()
if form.has_key("id"):      show_id(form.getlist("id"))
elif form.has_key("q"):     show_search(form.getlist("q"))
elif form.has_key("link"):  link(form)
else:
    print "<form action='' method='GET'>ID: <input name='id'><br>Name: <input name='q'><br>Scan: <input name='scan'></form>"
