def rename_stations(data_lines):
    """
    根据规则重命名台站名称
    
    规则：
    1. 台站代码为2位：重命名为台网代码(2位) + 台站代码，共4位
    2. 台站代码为3位：重命名为台网代码 + 台站代码，共5位
    3. 台站代码为5位：不进行重命名
    
    参数：
    data_lines: 包含台站数据的文本行列表
    
    返回：
    重命名后的数据行列表
    """
    renamed_lines = []
    
    for line in data_lines:
        # 跳过空行
        if not line.strip():
            renamed_lines.append(line)
            continue
            
        # 分割行数据
        parts = line.split()
        
        # 确保行有足够的字段（至少5个：纬度、经度、台网、台站、分量）
        if len(parts) < 5:
            renamed_lines.append(line)
            continue
            
        # 提取台网代码和台站代码
        network_code = parts[2]  # 台网代码（如HE、BJ、TJ等）
        station_code = parts[3]  # 台站代码
        
        # 根据台站代码长度应用不同的重命名规则
        station_length = len(station_code)
        
        if station_length == 2:
            # 规则1：2位台站代码 -> 台网代码(2位) + 台站代码 = 4位
            new_station_code = network_code[:2] + station_code
            parts[3] = new_station_code
        elif station_length == 3:
            # 规则2：3位台站代码 -> 台网代码 + 台站代码 = 5位
            new_station_code = network_code + station_code
            parts[3] = new_station_code
        elif station_length == 5:
            # 规则3：5位台站代码 -> 不重命名
            pass
        else:
            # 其他长度的台站代码，保持原样
            pass
        
        # 重新组合行
        renamed_line = ' '.join(parts)
        renamed_lines.append(renamed_line)
        renamed_lines.append('\n')
    
    return renamed_lines


def process_station_file(input_file, output_file):
    """
    处理台站数据文件
    
    参数：
    input_file: 输入文件路径
    output_file: 输出文件路径
    """
    try:
        # 读取输入文件
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 重命名台站
        renamed_lines = rename_stations(lines)
        
        # 写入输出文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(renamed_lines)
        
        print(f"处理完成！结果已保存到 {output_file}")
                
    except FileNotFoundError:
        print(f"错误：找不到文件 {input_file}")
    except Exception as e:
        print(f"处理过程中发生错误：{e}")


# 使用示例
if __name__ == "__main__":
    # 方法1：处理文件
    process_station_file('station.dat', 'station_renamed.dat')