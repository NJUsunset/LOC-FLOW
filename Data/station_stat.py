#!/usr/bin/env python3
"""
遍历目录中的所有rdseed.stations文件，提取台站信息，去重并合并到station.dat
同时检查同一台站是否有不同的经纬度，将多次重复合并为一条信息
并统计经纬度范围
"""

import os
import sys
import re
from pathlib import Path
from collections import defaultdict

def extract_channel_code(line):
    """从行中提取通道标记并标准化，使用更精确的规则"""
    # 使用正则表达式查找符合规则的通道代码模式
    # 第一个字符：E、H、B、L、S、M 其中之一
    # 第二个字符：H、L、N、D 其中之一
    # 第三个字符：N、E、Z 其中之一
    channel_pattern = r'\b([EHBLSM][HLND][NEZ])\b'
    matches = re.findall(channel_pattern, line)
    
    if matches:
        # 提取第一个匹配的通道代码
        channel_code = matches[0]
        # 标准化：取前两个字母加上'Z'
        standardized_code = channel_code[:2] + 'Z'
        return standardized_code
    else:
        return None

def parse_station_line(line):
    """解析单行台站信息，返回元组(台站代码, 网络代码, 纬度, 经度, 高程, 通道标记)"""
    parts = line.strip().split()
    if len(parts) < 4:
        return None
    
    # 前四个字段应该是：台站代码、网络代码、纬度、经度
    station = parts[0].strip()
    network = parts[1].strip()
    
    try:
        lat = float(parts[2])
        lon = float(parts[3])
    except ValueError:
        return None
    
    # 尝试提取高程（通常在第5列，如果存在）
    elevation = 0.0  # 默认值
    if len(parts) >= 5:
        try:
            elevation = float(parts[4]) / 1000.0  # 转换为km
        except ValueError:
            pass  # 如果无法解析高程，保持默认值
    
    # 提取通道标记
    channel_code = extract_channel_code(line)
    if channel_code is None:
        channel_code = "CHECK"
    
    return (station, network, lat, lon, elevation, channel_code)

def collect_station_files(root_dir):
    """收集所有rdseed.stations文件"""
    station_files = []
    root_path = Path(root_dir)
    
    print(f"在目录 {root_dir} 中搜索rdseed.stations文件...")
    
    for file_path in root_path.rglob('rdseed.stations'):
        if file_path.is_file():
            station_files.append(file_path)
    
    print(f"找到 {len(station_files)} 个rdseed.stations文件")
    return station_files

def process_station_files(station_files):
    """处理所有台站文件，返回去重后的台站信息和重复经纬度警告"""
    stations_dict = {}  # 用于存储最终选择的台站信息
    station_occurrences = defaultdict(list)  # 记录每个台站的所有出现位置
    total_stations = 0
    channel_warnings = []  # 记录通道标记警告
    
    for file_path in station_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    if line.strip() and not line.strip().startswith('#'):
                        station_info = parse_station_line(line)
                        if station_info:
                            total_stations += 1
                            station_key = (station_info[0], station_info[1])  # (台站代码, 网络代码)
                            
                            # 检查通道标记是否为CHECK
                            if station_info[5] == "CHECK":
                                channel_warnings.append({
                                    'file': str(file_path),
                                    'line': line_num,
                                    'station': station_info[0],
                                    'network': station_info[1],
                                    'content': line.strip()
                                })
                            
                            # 记录这个台站的出现
                            occurrence = {
                                'file': str(file_path),
                                'line': line_num,
                                'lat': station_info[2],
                                'lon': station_info[3],
                                'elevation': station_info[4],
                                'channel': station_info[5]
                            }
                            station_occurrences[station_key].append(occurrence)
                            
                            # 如果是第一次遇到这个台站，添加到最终字典
                            if station_key not in stations_dict:
                                stations_dict[station_key] = station_info
                                
        except Exception as e:
            print(f"错误: 无法读取文件 {file_path}: {e}")
    
    # 分析重复的台站
    duplicates = []
    for station_key, occurrences in station_occurrences.items():
        # 检查是否有不同的经纬度
        unique_locations = set((occ['lat'], occ['lon']) for occ in occurrences)
        if len(unique_locations) > 1:
            # 这个台站有多个不同的经纬度
            station_info = {
                'station': station_key[0],
                'network': station_key[1],
                'occurrences': occurrences,
                'unique_locations': list(unique_locations)
            }
            duplicates.append(station_info)
    
    # 提取stations_dict中的值作为唯一台站列表
    unique_stations = list(stations_dict.values())
    
    return unique_stations, duplicates, total_stations, channel_warnings

def calculate_coordinate_range(stations):
    """计算台站的经纬度范围"""
    if not stations:
        return None
    
    min_lat = max_lat = stations[0][2]
    min_lon = max_lon = stations[0][3]
    
    for station in stations:
        lat, lon = station[2], station[3]
        min_lat = min(min_lat, lat)
        max_lat = max(max_lat, lat)
        min_lon = min(min_lon, lon)
        max_lon = max(max_lon, lon)
    
    return {
        'min_lat': min_lat,
        'max_lat': max_lat,
        'min_lon': min_lon,
        'max_lon': max_lon,
        'lat_span': max_lat - min_lat,
        'lon_span': max_lon - min_lon
    }

def print_coordinate_range(coordinate_range):
    """打印经纬度范围统计"""
    if coordinate_range:
        print("\n" + "="*60)
        print("台站经纬度范围统计:")
        print("="*60)
        print(f"纬度范围: {coordinate_range['min_lat']:.5f}° ~ {coordinate_range['max_lat']:.5f}°")
        print(f"经度范围: {coordinate_range['min_lon']:.5f}° ~ {coordinate_range['max_lon']:.5f}°")
        print(f"纬度跨度: {coordinate_range['lat_span']:.5f}°")
        print(f"经度跨度: {coordinate_range['lon_span']:.5f}°")
        print("="*60)
    else:
        print("\n无法计算经纬度范围 - 没有有效的台站数据")

def write_stations_dat(stations, output_file='station.dat'):
    """将台站信息写入stations.dat文件，格式为: lat lon 网络代码 台站代码 通道标记 高程(km)"""
    with open(output_file, 'w', encoding='utf-8') as f:
        # 写入文件头
        # f.write("# 纬度 经度 网络代码 台站代码 通道标记 高程(km)\n")
        
        for station in stations:
            # 格式: lat lon network station channel elevation
            f.write(f"{station[2]:9.5f} {station[3]:9.5f} {station[1]:<4} {station[0]:<8} {station[5]:<4} {station[4]:7.3f}\n")
    
    print(f"台站信息已写入: {output_file}")

def print_duplicate_warnings(duplicates):
    """打印重复经纬度警告，将同一台站的多次重复合并为一条信息"""
    if duplicates:
        print("\n" + "="*80)
        print("警告: 发现以下台站具有不同的经纬度信息:")
        print("="*80)
        
        for dup in duplicates:
            print(f"\n台站: {dup['station']}.{dup['network']}")
            print(f"发现 {len(dup['unique_locations'])} 个不同的位置:")
            
            for i, (lat, lon) in enumerate(dup['unique_locations'], 1):
                print(f"  位置{i}: 纬度={lat:.5f}, 经度={lon:.5f}")
                
                # 显示这个位置出现的所有文件
                locations_with_this_coord = [occ for occ in dup['occurrences'] 
                                           if abs(occ['lat'] - lat) < 0.00001 and abs(occ['lon'] - lon) < 0.00001]
                for occ in locations_with_this_coord:
                    print(f"      - {occ['file']} (第{occ['line']}行)")
            
            print("-" * 60)
        
        print(f"\n总共发现 {len(duplicates)} 个台站存在经纬度不一致的情况")
    else:
        print("\n未发现同一台站具有不同经纬度的情况")

def print_channel_warnings(channel_warnings):
    """打印通道标记警告"""
    if channel_warnings:
        print("\n" + "="*80)
        print("警告: 以下台站行无法识别通道标记，已标记为'CHECK':")
        print("="*80)
        
        for warning in channel_warnings:
            print(f"台站: {warning['station']}.{warning['network']}")
            print(f"  文件: {warning['file']} (第{warning['line']}行)")
            print(f"  内容: {warning['content']}")
            print("-" * 40)
        
        print(f"\n总共发现 {len(channel_warnings)} 行无法识别通道标记")
    else:
        print("\n所有台站行都成功识别了通道标记")

def clean_dat_file(input_file, output_file=None):
    """
    清理dat文件：去除每行开头的空格并将分隔符统一为单个空格
    
    参数:
        input_file: 输入文件名
        output_file: 输出文件名（如果为None，则覆盖原文件）
    """
    if output_file is None:
        output_file = input_file
    
    # 读取并处理文件
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    # 处理每一行
    cleaned_lines = []
    for line in lines:
        # 去除开头和结尾的空格，并用单个空格分隔所有字段
        cleaned_line = ' '.join(line.strip().split())
        cleaned_lines.append(cleaned_line + '\n')
    
    # 写入输出文件
    with open(output_file, 'w') as f:
        f.writelines(cleaned_lines)
    
    print(f"文件处理完成！输出文件: {output_file}")

def main():
    if len(sys.argv) != 2:
        print("用法: python script.py <目录路径>")
        print("示例: python script.py /path/to/your/directory")
        sys.exit(1)
    
    root_dir = sys.argv[1]
    
    if not os.path.isdir(root_dir):
        print(f"错误: 目录不存在: {root_dir}")
        sys.exit(1)
    
    # 收集所有rdseed.stations文件
    station_files = collect_station_files(root_dir)
    
    if not station_files:
        print("未找到任何rdseed.stations文件")
        sys.exit(1)
    
    # 处理所有台站文件
    unique_stations, duplicates, total_count, channel_warnings = process_station_files(station_files)
    
    # 输出统计信息
    print(f"\n处理统计:")
    print(f"  总共解析台站记录: {total_count}")
    print(f"  去重后唯一台站数: {len(unique_stations)}")
    print(f"  发现重复经纬度台站: {len(duplicates)}")
    print(f"  无法识别通道标记的行数: {len(channel_warnings)}")
    
    # 计算并打印经纬度范围
    coordinate_range = calculate_coordinate_range(unique_stations)
    print_coordinate_range(coordinate_range)
    
    # 打印通道标记警告
    print_channel_warnings(channel_warnings)
    
    # 打印重复警告
    print_duplicate_warnings(duplicates)
    
    # 写入输出文件
    write_stations_dat(unique_stations)
    
    # 可选：按网络代码排序显示台站统计
    network_stats = {}
    channel_stats = {}
    for station in unique_stations:
        network = station[1]
        channel = station[5]
        network_stats[network] = network_stats.get(network, 0) + 1
        channel_stats[channel] = channel_stats.get(channel, 0) + 1
    
    print(f"\n台站网络分布:")
    for network, count in sorted(network_stats.items()):
        print(f"  {network}: {count} 个台站")
    
    print(f"\n通道标记分布:")
    for channel, count in sorted(channel_stats.items()):
        print(f"  {channel}: {count} 个台站")
    
    clean_dat_file("station.dat")

if __name__ == "__main__":
    main()