# quickbase-model-maker

![model_maker_logo](https://user-images.githubusercontent.com/38849824/181615187-f4682023-e299-429a-b444-eaad335d48a9.png)

---
A lightweight tool for creating and managing QuickBase models!

_Turn this_ 👎
```python
# select relevant info
select = [3, 43, 23, 63, 21, 52, 24, 54]
```

_Into this_ 👍
```python
from references.order_manager import Order
select = [
    Order.RECORD_ID,
    Order.ORDER_TYPE,
    Order.ORDER_NUMBER,
    Order.DELIVERY_DATE
    ...
]
```

_With just a few lines of code!_

---

## Installation

```bash
pip install quickbase-model-maker
```

## Usage

### Initializing

The sample code below will initialize your models for use in your application.  Models are created within their respective app folders, in a new directory called `references`.

```python
# import model maker
from quickbase_model_maker import ModelMaker

# create model maker with realm and auth info
qmm = ModelMaker(realm='realm', auth='AUTH-TOKEN')

# register tables you wish to create models from
qmm.register_tables([
    ('bqs5asdf', 'bqs5aser'), # ('app_id', 'table_id') tuples
    ('bqs5abzc', 'brzaners'),
    ('bqs5abzc', 'brzanvac'),
    ('bqs5abzc', 'bqs5wers'),
])
```

Generate your models, based off of the registered tables, with the `.sync()` method.

```python
# call sync method to create models
qmm.sync(only_new_tables=True)
```

Optionally, you can sync all registered tables, regardless of whether they have already been synced.
It is recommended to call `.sync()` 
only when you wish to re-generate models, as **each model sync with Quickbase costs 1 API call**. You only have to generate 
models once - or when you wish to update your models (i.e. new field you need to access added on quickbase).  Calling `.sync()` on 
every script run **could result in a large number of API calls**.

```python
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

### Removing Models

Models can easily be removed by doing the following:
- Remove the model from the `references/app` directory
- Remove the related table from the `references/__init__.py` file.
- Remove the related table tuple from the `.register_tables()` method.