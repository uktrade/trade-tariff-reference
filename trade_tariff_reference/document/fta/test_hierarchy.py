from hierarchy import hierarchy

import sys
import glob as g
import functions as f

# Set up
app = g.app
goods_nomenclature_item_id = "0805102200"
productline_suffix = "80"

sql = """SELECT goods_nomenclature_item_id, producline_suffix as productline_suffix, number_indents,
description FROM ml.goods_nomenclature_export('0805102200') WHERE producline_suffix = '80';"""
cur = app.conn.cursor()
cur.execute(sql)
rows = cur.fetchall()
for row in rows:
    number_indents = row[2]
    description = row[3]
    print (number_indents)
    hier = hierarchy(goods_nomenclature_item_id, productline_suffix, number_indents, description)
    hier.get_hierarchy("up")
    clause = ""
    for o in hier.ar_hierarchies:
        print (o.goods_nomenclature_item_id, o.productline_suffix)
        if o.productline_suffix == "80":
            clause += "'" + o.goods_nomenclature_item_id + "', "
    clause = clause.strip()
    clause = clause.strip(",")
    print (clause)

sql = """SELECT * FROM measures WHERE goods_nomenclature_item_id IN (""" + clause + """) AND measure_type_id IN ('103', '105')
AND validity_start_date < '2019_03_29' AND (validity_end_date >= '2019_03_29' OR validity_end_date IS NULL)"""

"""
Next steps
==========
Having got the list of commodity code higher in the hierarchy tree that we want to search for MFNs
against, we now need to actually get the MFNs themselves. In certain cases, the MFN will exist as measure components
however in most cases, this will not be the case, as they will exist as measure_condition_components

Thought
=======
Might need to make the search below specifically against the times at which the duties in the FTA schedule are applicable
This is almost entirely impossible

"""


sql = """SELECT * FROM measures WHERE goods_nomenclature_item_id IN (""" + clause + """) AND measure_type_id IN ('103', '105')
AND validity_start_date < '2019_03_29' AND (validity_end_date >= '2019_03_29' OR validity_end_date IS NULL)"""
print (sql)
sys.exit()
"""
cur = app.conn.cursor()
cur.execute(sql)
rows = cur.fetchall()
for row in rows:
"""