# -*- coding: utf-8 -*-
def alltemplates():
    temps=db(db.template.id>=0).select()
    return temps

def allisos():
    iso=db(db.isofile.id>=0).select()
    return iso

