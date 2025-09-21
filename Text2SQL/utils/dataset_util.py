from decimal import Decimal

def rows_to_dicts(cursor, rows):
    """
    把 SQL 查询结果转换成 {"execute_info": [...]}
    - cursor.description 提供列名
    - Decimal 自动转 float
    """
    columns = [desc[0] for desc in cursor.description]
    result = []
    for row in rows:
        item = {}
        for col, val in zip(columns, row):
            if isinstance(val, Decimal):
                val = float(val)
            item[col] = val
        result.append(item)
    return result
