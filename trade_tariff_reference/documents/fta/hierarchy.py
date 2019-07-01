import glob as g


class hierarchy(object):
	def __init__(self, goods_nomenclature_item_id, productline_suffix, description, number_indents):
		# Get parameters from instantiator
		self.goods_nomenclature_item_id = goods_nomenclature_item_id
		self.productline_suffix         = productline_suffix
		self.description               	= description
		self.number_indents             = number_indents

	def get_hierarchy(self, direction):
		ar_goods_nomenclatures = []
		ar_hierarchies = []
		stem = self.goods_nomenclature_item_id[0:2]
		sql = "SELECT goods_nomenclature_item_id, producline_suffix as productline_suffix, number_indents, description FROM ml.goods_nomenclature_export('" + stem + "%') ORDER BY goods_nomenclature_item_id, producline_suffix"
		cur = g.app.conn.cursor()
		cur.execute(sql)
		rows = cur.fetchall()
		
		cnt = 0
		for row in rows:
			goods_nomenclature_item_id = row[0]
			productline_suffix         = row[1]
			number_indents             = row[2]
			description		           = row[3]
			gn = hierarchy(goods_nomenclature_item_id, productline_suffix, description, number_indents)
			gn.deal_with_double_zeroes()
			ar_goods_nomenclatures.append(gn)

			#print (goods_nomenclature_item_id, productline_suffix, cnt)
			cnt += 1
		#sys.exit()


		record_count = len(ar_goods_nomenclatures)
		for commodity in ar_goods_nomenclatures:
			if ((commodity.goods_nomenclature_item_id == self.goods_nomenclature_item_id) and (commodity.productline_suffix == self.productline_suffix)):
				my_index	= ar_goods_nomenclatures.index(commodity)
				#print (my_index)
				my_indent	= commodity.number_indents
				break


		# Kludge to deal with the chapter level records, which have a "0" indent, the same as their children
		if (my_indent == 0):
			if (self.goods_nomenclature_item_id[-8:] == "00000000"):
				#print ("found 0") # Try this later
				my_indent = -1

		# First, search up towards the root of the tree from my_index to find parent codes
		temp_indent = my_indent
		for i in range(my_index, 0, -1):
			t = ar_goods_nomenclatures[i]
			if ((t.number_indents < temp_indent) or ((t.goods_nomenclature_item_id == self.goods_nomenclature_item_id) and (t.productline_suffix == self.productline_suffix))):
				ar_hierarchies.append(t)
				temp_indent = t.number_indents

		# Reverse the hierarchy, so that the 'current' hierarchical item sits at the bottom
		ar_hierarchies.reverse()
		hier_count = len(ar_hierarchies)
		# Remove the empty item accidentally created when the array was initialised
		#if (hier_count > 0):
		#	ar_hierarchies.pop(hier_count) # Not necessary - this is just an issue in PHP

		# Then search down towards the branches of the tree from my_index to find child codes
		if direction != "up":
			temp_indent = my_indent
			for i in range(my_index + 1, record_count):
				t = ar_goods_nomenclatures[i]
				if (t.number_indents <= my_indent):
					break
				else:
					ar_hierarchies.append(t)

		self.ar_hierarchies = ar_hierarchies

	def deal_with_double_zeroes(self):
		if (self.number_indents == 0):
			if (self.goods_nomenclature_item_id[-8:] == "00000000"):
				self.number_indents = -1
