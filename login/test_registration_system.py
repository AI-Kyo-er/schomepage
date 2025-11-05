#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
注册系统功能测试脚本
测试清单文件处理、用户文件夹创建和CSV操作
"""

import os
import sys
import json
import shutil
from server import (
    load_registration_checklist, 
    create_user_folders, 
    write_users_csv_with_maxarticle,
    read_users_csv_with_maxarticle
)

def test_checklist_loading():
    """测试清单文件加载"""
    print("=" * 50)
    print("🧪 测试1: 清单文件加载")
    print("=" * 50)
    
    checklist = load_registration_checklist()
    if checklist:
        print("✅ 清单文件加载成功")
        print(f"📋 描述: {checklist.get('description', 'N/A')}")
        print(f"📝 版本: {checklist.get('version', 'N/A')}")
        
        # 检查CSV操作配置
        csv_ops = checklist['operations']['csv_operations']
        print(f"📊 CSV文件: {csv_ops['file']}")
        print(f"📊 列配置: {len(csv_ops['columns'])} 列")
        for col in csv_ops['columns']:
            print(f"   - {col['name']}: {col['type']}")
        
        # 检查文件夹操作配置
        folder_ops = checklist['operations']['folder_operations']
        print(f"📁 基础路径: {folder_ops['base_path']}")
        print(f"📁 创建文件夹: {len(folder_ops['folders_to_create'])} 个")
        for folder in folder_ops['folders_to_create']:
            print(f"   - {folder['path']}")
        
        return checklist
    else:
        print("❌ 清单文件加载失败")
        return None

def test_csv_operations():
    """测试CSV操作"""
    print("\n" + "=" * 50)
    print("🧪 测试2: CSV文件操作")
    print("=" * 50)
    
    # 备份原始CSV文件
    backup_file = 'users.csv.backup'
    if os.path.exists('users.csv'):
        shutil.copy2('users.csv', backup_file)
        print(f"✅ 备份原始CSV文件为: {backup_file}")
    
    try:
        # 读取现有数据
        print("📖 读取现有用户数据...")
        users = read_users_csv_with_maxarticle()
        print(f"✅ 读取到 {len(users)} 个用户")
        for username, data in users.items():
            print(f"   - {username}: maxarticle={data['maxarticle']}")
        
        # 添加测试用户
        test_username = "test_user@example.com"
        users[test_username] = {
            'password': 'test_encrypted_password',
            'maxarticle': 30
        }
        
        # 写入CSV
        print(f"📝 添加测试用户: {test_username}")
        if write_users_csv_with_maxarticle(users):
            print("✅ CSV写入成功")
            
            # 验证写入结果
            users_verify = read_users_csv_with_maxarticle()
            if test_username in users_verify:
                print(f"✅ 测试用户验证成功: maxarticle={users_verify[test_username]['maxarticle']}")
            else:
                print("❌ 测试用户验证失败")
        else:
            print("❌ CSV写入失败")
        
        # 移除测试用户
        if test_username in users:
            del users[test_username]
            write_users_csv_with_maxarticle(users)
            print(f"🗑️  移除测试用户: {test_username}")
        
    except Exception as e:
        print(f"❌ CSV操作测试失败: {e}")
    
    # 恢复原始CSV文件
    if os.path.exists(backup_file):
        shutil.copy2(backup_file, 'users.csv')
        os.remove(backup_file)
        print(f"🔄 恢复原始CSV文件")

def test_folder_creation():
    """测试文件夹创建"""
    print("\n" + "=" * 50)
    print("🧪 测试3: 用户文件夹创建")
    print("=" * 50)
    
    checklist = load_registration_checklist()
    if not checklist:
        print("❌ 无法加载清单文件，跳过文件夹测试")
        return
    
    test_username = "test_folder_user"
    test_base_path = "../workplace"
    test_user_path = os.path.join(test_base_path, test_username)
    
    # 确保测试文件夹不存在
    if os.path.exists(test_user_path):
        shutil.rmtree(test_user_path)
        print(f"🗑️  清理现有测试文件夹: {test_user_path}")
    
    try:
        # 创建用户文件夹
        print(f"📁 为用户 '{test_username}' 创建文件夹...")
        if create_user_folders(test_username, checklist):
            print("✅ 文件夹创建成功")
            
            # 验证文件夹结构
            expected_folders = [
                test_user_path,
                os.path.join(test_user_path, "article"),
                os.path.join(test_user_path, "pics")
            ]
            
            all_exist = True
            for folder in expected_folders:
                if os.path.exists(folder):
                    print(f"✅ 验证文件夹存在: {folder}")
                else:
                    print(f"❌ 文件夹不存在: {folder}")
                    all_exist = False
            
            if all_exist:
                print("🎉 文件夹结构验证成功")
            else:
                print("❌ 文件夹结构验证失败")
            
            # 测试冲突处理
            print("\n🔄 测试冲突处理（保留现有文件夹）...")
            if create_user_folders(test_username, checklist):
                print("✅ 冲突处理成功（保留现有文件夹）")
            else:
                print("❌ 冲突处理失败")
        else:
            print("❌ 文件夹创建失败")
    
    except Exception as e:
        print(f"❌ 文件夹创建测试失败: {e}")
    
    finally:
        # 清理测试文件夹
        if os.path.exists(test_user_path):
            shutil.rmtree(test_user_path)
            print(f"🗑️  清理测试文件夹: {test_user_path}")

def test_complete_registration_process():
    """测试完整的注册流程"""
    print("\n" + "=" * 50)
    print("🧪 测试4: 完整注册流程模拟")
    print("=" * 50)
    
    checklist = load_registration_checklist()
    if not checklist:
        print("❌ 无法加载清单文件，跳过完整测试")
        return
    
    test_email = "full_test@example.com"
    test_password = "test_encrypted_pwd"
    
    # 备份原始CSV
    backup_file = 'users.csv.backup_full'
    if os.path.exists('users.csv'):
        shutil.copy2('users.csv', backup_file)
    
    try:
        print(f"👤 模拟注册用户: {test_email}")
        
        # 1. 读取现有用户
        users = read_users_csv_with_maxarticle()
        original_count = len(users)
        print(f"📊 当前用户数量: {original_count}")
        
        # 2. 获取默认maxarticle值
        csv_config = checklist['operations']['csv_operations']
        maxarticle_default = 30
        for column in csv_config['columns']:
            if column['name'] == 'maxarticle' and column['type'] == 'default_value':
                maxarticle_default = column['value']
                break
        
        # 3. 添加新用户
        users[test_email] = {
            'password': test_password,
            'maxarticle': maxarticle_default
        }
        
        # 4. 写入CSV
        if not write_users_csv_with_maxarticle(users):
            print("❌ CSV写入失败")
            return
        print(f"✅ CSV更新成功，maxarticle: {maxarticle_default}")
        
        # 5. 创建用户文件夹
        if not create_user_folders(test_email, checklist):
            print("❌ 文件夹创建失败")
            return
        print("✅ 用户文件夹创建成功")
        
        # 6. 验证最终结果
        users_verify = read_users_csv_with_maxarticle()
        if test_email in users_verify:
            user_data = users_verify[test_email]
            print(f"✅ 注册验证成功:")
            print(f"   - 用户名: {test_email}")
            print(f"   - 密码: {user_data['password']}")
            print(f"   - maxarticle: {user_data['maxarticle']}")
            print(f"   - 总用户数: {len(users_verify)} (增加 {len(users_verify) - original_count})")
        else:
            print("❌ 注册验证失败：用户不存在")
        
        # 验证文件夹结构
        test_user_path = os.path.join("../workplace", test_email)
        folders_to_check = [
            test_user_path,
            os.path.join(test_user_path, "article"),
            os.path.join(test_user_path, "pics")
        ]
        
        folder_check_passed = True
        for folder in folders_to_check:
            if os.path.exists(folder):
                print(f"✅ 文件夹验证: {folder}")
            else:
                print(f"❌ 文件夹缺失: {folder}")
                folder_check_passed = False
        
        if folder_check_passed:
            print("🎉 完整注册流程测试成功！")
        else:
            print("⚠️  注册成功但文件夹结构不完整")
    
    except Exception as e:
        print(f"❌ 完整注册流程测试失败: {e}")
    
    finally:
        # 清理测试数据
        if os.path.exists(backup_file):
            shutil.copy2(backup_file, 'users.csv')
            os.remove(backup_file)
            print("🔄 恢复原始CSV文件")
        
        # 清理测试文件夹
        test_user_path = os.path.join("../workplace", test_email)
        if os.path.exists(test_user_path):
            shutil.rmtree(test_user_path)
            print(f"🗑️  清理测试文件夹")

def main():
    """主测试函数"""
    print("🚀 注册系统功能测试开始")
    print(f"📍 当前工作目录: {os.getcwd()}")
    
    # 检查必要文件
    required_files = ['registration_checklist.json', 'server.py']
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少必要文件: {missing_files}")
        return
    
    try:
        # 执行所有测试
        test_checklist_loading()
        test_csv_operations()
        test_folder_creation()
        test_complete_registration_process()
        
        print("\n" + "=" * 50)
        print("🎉 所有测试完成！")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 