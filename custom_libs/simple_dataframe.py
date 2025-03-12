class DataFrame:
    def __init__(self, data=None, columns=None):
        """
        初始化 DataFrame
        
        Args:
            data: 可选，初始数据（行列表）
            columns: 列名称列表
        """
        self.columns = columns if columns else []
        self.data = []
        
        if data:
            for row in data:
                if isinstance(row, dict):
                    self.data.append([row.get(col, None) for col in self.columns])
                else:
                    self.data.append(row)
    
    def _append(self, row_dict, ignore_index=False):
        """
        添加一行数据
        
        Args:
            row_dict: 包含行数据的字典
            ignore_index: 是否忽略索引（兼容pandas接口，实际未使用）
            
        Returns:
            返回添加行后的新 DataFrame
        """
        new_df = DataFrame(columns=self.columns)
        new_df.data = self.data.copy()
        
        # 将字典转换为列表并添加
        new_row = [row_dict.get(col, None) for col in self.columns]
        new_df.data.append(new_row)
        
        return new_df
    
    def drop_duplicates(self, subset=None):
        """
        删除重复行
        
        Args:
            subset: 用于判断重复的列名列表
            
        Returns:
            返回去重后的新 DataFrame
        """
        if not subset:
            subset = self.columns
            
        # 获取子集索引
        subset_indices = [self.columns.index(col) for col in subset if col in self.columns]
        
        # 使用集合去重
        unique_keys = set()
        unique_data = []
        
        for row in self.data:
            # 创建用于判断重复的键
            key = tuple(row[i] for i in subset_indices)
            
            if key not in unique_keys:
                unique_keys.add(key)
                unique_data.append(row)
        
        # 创建新的 DataFrame
        result = DataFrame(columns=self.columns)
        result.data = unique_data
        
        return result

    def to_csv(self, path, index=False, encoding='utf-8'):
        """
        将DataFrame保存为CSV文件
        
        Args:
            path: 要保存的文件路径
            index: 是否包含索引列，默认False
            encoding: 文件编码，默认'utf-8'
        """
        import csv
        
        with open(path, 'w', newline='', encoding=encoding) as f:
            writer = csv.writer(f)
            
            # 写入列名
            writer.writerow(self.columns)
            
            # 写入数据
            for row in self.data:
                writer.writerow(row)

    def __str__(self):
        """返回 DataFrame 的字符串表示"""
        lines = ['\t'.join(str(x) for x in self.columns)]
        for row in self.data:
            lines.append('\t'.join(str(x) for x in row))
        return '\n'.join(lines)
    
    def to_dict(self, orient='records'):
        """
        将 DataFrame 转换为字典列表
        
        Args:
            orient: 转换方向，支持 'records'
            
        Returns:
            字典列表
        """
        if orient == 'records':
            result = []
            for row in self.data:
                row_dict = {col: row[i] for i, col in enumerate(self.columns)}
                result.append(row_dict)
            return result
        else:
            raise ValueError("只支持 'records' 方向")