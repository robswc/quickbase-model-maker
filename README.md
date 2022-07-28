# quickbase-model-maker

![model_maker_logo](https://user-images.githubusercontent.com/38849824/181615187-f4682023-e299-429a-b444-eaad335d48a9.png)


## Usage

### Initializing

The sample code below will initialize your models for use in your application.  **Registering tables costs 1 API call per table.  You do not have to register your tables
upon every script run.**  It is recommended that you register your tables and sync only once (or when you wish to update your models) via the python terminal.

```python
# import model maker
from quickbase_model_maker.model_maker import QuickbaseModelMaker

# create model maker with realm and auth info
qmm = QuickbaseModelMaker(realm='realm', auth='AUTH-TOKEN')

# register tables you wish to create models from
qmm.register_tables([
    ('bqs5asdf', 'bqs5aser'), # ('app_id', 'table_id') tuples
    ('bqs5abzc', 'brzaners'),
    ('bqs5abzc', 'brzanvac'),
    ('bqs5abzc', 'bqs5wers'),
])

# call sync method to create models
qmm.sync()

```

### In code

Once registered and created, models can be used in your application.  
The following code uses a fictional "Order" model to demonstrate 
how one can access the `ORDER_TYPE` field.  One can also access useful metadata
through methods like `.table_id()` and `.app_id()`.

```python
from references.orders import Order
print(Order.ORDER_TYPE)
print(Order.table_id())
```
