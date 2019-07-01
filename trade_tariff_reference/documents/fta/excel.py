import xlsxwriter, psycopg2

workbook = xlsxwriter.Workbook('hello.xlsx')
worksheet = workbook.add_worksheet()
bold = workbook.add_format({'bold': True})
wrap = workbook.add_format({'text_wrap': True, 'align': 'left', 'valign': 'top'})

indents = []
for i in range(0, 14):
	tmp = workbook.add_format({'text_wrap': True, 'align': 'left', 'valign': 'top', 'indent': i*2})
	indents.append(tmp)

DBASE = "tariff_eu"
p = "zanzibar"
conn = psycopg2.connect("dbname=" + DBASE + " user=postgres password=" + p)


# Get the MFNs
sql = """select * from ml.v5 m, measure_components mc
where m.measure_sid = mc.measure_sid
and m.measure_type_id in ('103', '105')
and goods_nomenclature_item_id like '01%'
order by goods_nomenclature_item_id"""
cur = conn.cursor()
cur.execute(sql)
rows_mfns = cur.fetchall()

# Get the nomenclature
sql = """
SELECT * from ml.goods_nomenclature_export3('%') ORDER BY 2, 3
"""

cur = conn.cursor()
cur.execute(sql)
rows = cur.fetchall()
rowcount = 2
worksheet.write('A1', 'Commodity code', bold)
worksheet.write('B1', 'Product line suffix', bold)
worksheet.write('C1', 'Description', bold)
worksheet.write('D1', 'Indent', bold)

worksheet.set_column('A:A', 20)
worksheet.set_column('B:B', 15)
worksheet.set_column('C:C', 50)

for row in rows:
	goods_nomenclature_item_id  = row[1]
	producline_suffix           = row[2]
	description                 = row[5]
	indent                      = row[6]
	address1 = "A" + str(rowcount)
	address2 = "B" + str(rowcount)
	address3 = "C" + str(rowcount)
	address4 = "D" + str(rowcount)
	worksheet.write(address1, goods_nomenclature_item_id, wrap)
	worksheet.write(address2, producline_suffix, wrap)
	worksheet.write(address3, description, indents[indent])
	worksheet.write(address4, indent, wrap)
	rowcount += 1


worksheet.freeze_panes(1, 0)
workbook.close()