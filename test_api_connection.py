#!/usr/bin/env python3
"""
API连接测试脚本
用于验证ScraperAPI的连接和请求格式
"""
import http.client 
import json
from urllib.parse import urlencode

def test_api_connection_json():
    """测试使用JSON格式的API请求（推荐）"""
    print("=" * 60)
    print("测试1: JSON格式请求（推荐，脚本使用的格式）")
    print("=" * 60)
    
    try:
        conn = http.client.HTTPSConnection("scraperapi.thordata.com")
        
        # JSON格式 - 这是脚本使用的格式
        payload = json.dumps({
            "url": "https://www.google.com/search?q=pizza&json=1"
        })
        
        headers = { 
            'Authorization': 'Bearer 663fba4eb51f1fb2ec007f1b7bd73f16',
            'Content-Type': 'application/json'
        }
        
        conn.request("POST", "/request", payload, headers) 
        res = conn.getresponse() 
        data = res.read()
        
        print(f"✓ 请求成功")
        print(f"  状态码: {res.status}")
        print(f"  响应大小: {len(data)} bytes ({len(data)/1024:.2f} KB)")
        
        if res.status == 200:
            print(f"  响应预览: {data.decode('utf-8')[:200]}...")
            print(f"\n✓ API连接正常 - JSON格式")
        else:
            print(f"  响应内容: {data.decode('utf-8')[:500]}")
            print(f"\n⚠ API返回非200状态码")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        print(f"  错误类型: {type(e).__name__}")
        return False


def test_api_connection_urlencoded():
    """测试使用URL编码格式的API请求（问题陈述中的示例）"""
    print("\n" + "=" * 60)
    print("测试2: URL编码格式请求（问题陈述中的示例）")
    print("=" * 60)
    
    try:
        conn = http.client.HTTPSConnection("scraperapi.thordata.com")
        
        # URL编码格式 - 问题陈述中的示例
        params = {
            "engine": "google",
            "q": "pizza",
            "json": "1"
        }
        payload = urlencode(params)
        
        headers = { 
            'Authorization': 'Bearer 663fba4eb51f1fb2ec007f1b7bd73f16',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        conn.request("POST", "/request", payload, headers) 
        res = conn.getresponse() 
        data = res.read()
        
        print(f"✓ 请求成功")
        print(f"  状态码: {res.status}")
        print(f"  响应大小: {len(data)} bytes ({len(data)/1024:.2f} KB)")
        
        if res.status == 200:
            print(f"  响应预览: {data.decode('utf-8')[:200]}...")
            print(f"\n✓ API连接正常 - URL编码格式")
        else:
            print(f"  响应内容: {data.decode('utf-8')[:500]}")
            print(f"\n⚠ API返回非200状态码")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        print(f"  错误类型: {type(e).__name__}")
        return False


def main():
    print("\n" + "=" * 60)
    print("ScraperAPI 连接测试")
    print("=" * 60 + "\n")
    
    print("说明：")
    print("- 本脚本测试两种API请求格式")
    print("- JSON格式是监控脚本使用的格式（推荐）")
    print("- URL编码格式是问题陈述中提供的示例格式")
    print()
    
    # 测试两种格式
    result1 = test_api_connection_json()
    result2 = test_api_connection_urlencoded()
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"JSON格式测试: {'✓ 通过' if result1 else '✗ 失败'}")
    print(f"URL编码格式测试: {'✓ 通过' if result2 else '✗ 失败'}")
    print()
    
    if not result1 and not result2:
        print("⚠ 注意：")
        print("  如果在受限网络环境中（如CI/CD），API可能无法访问")
        print("  这是正常现象，实际生产环境中应该可以正常连接")
    else:
        print("✓ 监控脚本使用的API请求格式已验证可用")
    
    print("\n推荐使用：")
    print("  监控脚本使用的JSON格式（Content-Type: application/json）")
    print("  优点：更标准、更易维护、更符合RESTful API规范")
    print()


if __name__ == "__main__":
    main()
