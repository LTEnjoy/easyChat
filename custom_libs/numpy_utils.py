def arange(start, stop, step=1):
    """
    生成一个等差数列，类似numpy.arange的功能。
    
    参数:
        start: 起始值
        stop: 结束值（不包含）
        step: 步长（默认为1）
    
    返回:
        包含等差数列的列表
    """
    # 处理浮点数精度问题
    if isinstance(step, float) or isinstance(start, float) or isinstance(stop, float):
        # 计算元素个数，使用round避免浮点数精度问题
        n = round((stop - start) / step)
        return [start + i * step for i in range(n + 1)]
    else:
        # 对于整数，使用传统的range
        return list(range(start, stop, step))