from dataclasses import dataclass, fields
@dataclass(kw_only=True)
class Configuration:
    relation_table_count:int=5