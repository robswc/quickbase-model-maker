# quickbase-model-maker

```python
qmm = QuickbaseModelMaker('realm', 'userToken')

qmm.register_tables(
    [
        ('bqs6asdf', 'bqs8asdf'),  # order records
        ('bqs6asdf', 'brzasdf')  # shipment records
    ]
)

# call sync initally at least once.  Plans to implement proper migrations and sycn on schedule in future!
qmm.sync()
```

```python
from references.orders import Order
print(Order.ORDER_TYPE)
print(Order.get_table_id())
```
