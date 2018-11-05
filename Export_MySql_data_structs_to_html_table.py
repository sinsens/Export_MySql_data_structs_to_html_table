"""
魔改自：https://github.com/yanglikun/mysql2word-python
于Windows 10 + Python 3.5.4环境下测试通过
"""
__author__ = 'Sinsen'
from sqlalchemy import create_engine

# 数据库配置
dbConfig = {
	'userName':'userName',
	'password':'',
	'host':'127.0.0.1',
	'port':'3306',
	'databaseName':'databaseName',
	'charset':'utf8'
}

# HTML Table
table_header = """
<table border=1>
<tr><td>表名</td><td colspan='3'>%s (%s)</td></tr>
<tr>
<td>列名</td>
<td>类型</td>
<td>是否主键</td>
<td>备注</td>
</tr>
"""	
table_body = """
<tr>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
</tr>"""

class Field:
	def __init__(self, name=None, type=None, comment=None, nullable=None, isPK=None):
		super().__init__()
		self.name = name
		self.type = type
		self.comment = comment
		self.nullable = nullable
		self.isPK = isPK


class Index:
	def __init__(self, isUnique=None, name=None, seqNO=None, fieldName=None, comment=None):
		super().__init__()
		self.comment = comment
		self.fieldName = fieldName
		self.seqNO = seqNO
		self.name = name
		self.isUnique = isUnique


class Table:
	def __init__(self, name=None, comment=None):
		self.name = name
		self.fields = []
		self.indices = []
		self.comment = comment

	def addField(self, field):
		self.fields.append(field)

	def addIndex(self, index):
		self.indices.append(index)


class MySql:
	def __init__(self):
		dburl = "mysql+pymysql://{userName}:{password}@{host}:{port}/{databaseName}?charset={charset}".format(
			**dbConfig
		)
		self.engine = create_engine(dburl)

	def showTables(self):
		return [ele[0] for ele in self.engine.execute('show tables')]

	def tableDetail(self, tableName):
		fields = []
		for fieldRow in self.engine.execute('show full columns from ' + tableName):
			field = Field()
			field.name = fieldRow['Field']
			field.type = str(fieldRow['Type']).lower()
			field.nullable = fieldRow['Null']
			field.isPK = fieldRow['Key'] == 'PRI'
			field.comment = fieldRow['Comment']
			field.default = fieldRow['Default']
			field.extra = fieldRow['Extra']
			fields.append(field)
		tableComment = ''
		for ele in self.engine.execute('show table status where name="' + tableName + '"'):
			tableComment = ele['Comment']
		indices = []
		for idx in self.engine.execute('show index from ' + tableName):
			index = Index()
			index.isUnique = (idx['Non_unique'] == 0)
			index.name = str(idx['Key_name'])
			fieldName = idx['Column_name']
			index.fieldName = str(fieldName).lower()
			index.comment = idx['Comment']
			index.seqNO = str(idx['Seq_in_index'])
			index.type = idx['Index_type']
			indices.append(index)

		table = Table(tableName)
		table.fields = fields
		table.indices = indices
		table.comment = tableComment
		return table

	def generateTableData(self):
		tableNames = self.showTables()
		return [self.tableDetail(tableName) for tableName in tableNames]

	def close(mysql):
		if mysql is None:
			return
		try:
			mysql.engine.dispose()
		except Exception as ex:
			print("发生错误：", ex)

try:
	with open('tables.html', 'w') as f:
		mysql = MySql()
		table_num = 0	# 总共表数
		field_total = 0 # 总共字段数
		for i in mysql.showTables():
			table_num += 1
			field_num = 0
			table = mysql.tableDetail(i)
			#print(table_header % (i, table.comment))
			f.write("<html><head><title>数据库%s设计说明</title></head><body>"%dbConfig["databaseName"]) # 写入HTML开始标签
			f.write(table_header % (i, table.comment)) # 写入TABLE开始标签
			
			for field in table.fields:
				# 主键判断
				isPk = ""
				if field.isPK:
					isPk = "是"
				f.write(table_body % (field.name, field.type, isPk, field.comment))	# 写入body
				field_num+=1
				field_total+=1
			print("写入表: ", i, "\t\t该表共", len(table.fields), "个字段，已写入", field_num, "个字段")
			f.write("</table><br/><br/>\n\n") # 写入TABLE结束标签
		f.write("</body></html>") # 写入HTML结束标签
		f.flush()
		f.close()
		mysql.close()	# 关闭数据库连接
		print("写入完成，共写入",table_num,"张表的信息，共有", field_total, "个字段")
except Exception as ex:
	print("发生错误：", ex)