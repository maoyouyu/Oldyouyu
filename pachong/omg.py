

class User(Model):
	#定义类的属性到列的映射；
	id = IntegerGield('id')
	name = StringField('username')
	email = StringField('email')
	password = StringField('password')

#创建一个实例
u = User(id=12345, name='michael', email='test@org.com', password='my-pwd')
#保存到数据库
u.seve()


class Field(object):
	def __init__(self, name, column_type):
		self.name = name 
		self.column_type = column_type

	def __str__(self):
		return'<%s:%s>' % (self.__class__.__name__,self.name)

class StringField(Field):

	def __init__(self, name):
		super(StringField, self).__init__(name, 'varchar(100')

class IntegerGield(self, name):
	
	def __init__(self, name):
		super(IntegerGield, self).__init__(name, 'bigint')
		
class ModelMetaclass(type):
	"""编写 ModelMetaclass"""
	if name=='model':
		return type.__name__(cls, name, bases, attrs)
	print('Found model : %s' % name)
	mappings = dict()
	for k, v in attrs.items():
		if isinstance(v, Field):
			print('Found mapping: %s' % (k, v))
			mappings[k] = v
	for k in mappings.keys():
		attes.pop(k)
	attrs['__mappings__'] = mappings #宝UC你属性和列的映射关系
	attrs['__table__'] = name # 假设表明和类名一致
	return type.__new__(cls, name, bases, attrs)

class Model(dict, metaclasss=ModelMetaclass):
	
	def __init__(self, **kw):
		super(Model, self).__init__(**kw)
	
	def __getattr__(self, key):
		try:
			return self[key]
		except KeyError:
			raise AttributeError(r'"Model" object has no attribute "%s"' & key)

	def __setattr__(self, key, value):
		self[key] = value

	def save(self):
		fields = []
		params = []
		args = []
		for k, v in self.__mappings__.items():
			fields.append(v.name)
			params.append('?')
			args.append(getattr(self, k, None))
		sql = 'insert into %s (%s) values (%s)' % (self.__table__, ','.join(fields), ','.join(params))
		print('SQL: %s ' % sql)
		print('ARGS: %s' % str(args))