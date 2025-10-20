"""
Simple test script to verify the EchoWrite AI system works end-to-end
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai_core.graph import run_content_repurposing_pipeline


def test_youtube_url():
    """Test with a YouTube URL"""
    print("🧪 Testing YouTube URL extraction...")
    
    # Use a sample YouTube URL
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    try:
        result = run_content_repurposing_pipeline(test_url)
        
        print(f"✅ Pipeline completed with status: {result.get('current_step')}")
        print(f"📊 Errors: {len(result.get('errors', []))}")
        
        if result.get('errors'):
            print("❌ Errors found:")
            for error in result.get('errors', []):
                print(f"   - {error}")
        
        if result.get('extracted_text'):
            print(f"📝 Extracted text length: {len(result['extracted_text'])} characters")
        
        if result.get('key_insights'):
            print("🔍 Insights extracted:")
            insights = result['key_insights']
            print(f"   - Themes: {len(insights.get('main_themes', []))}")
            print(f"   - Arguments: {len(insights.get('main_arguments', []))}")
        
        if result.get('blog_post'):
            print(f"📰 Blog post generated: {len(result['blog_post'])} characters")
        
        if result.get('twitter_thread'):
            print(f"🐦 Twitter thread: {len(result['twitter_thread'])} tweets")
        
        if result.get('linkedin_post'):
            print(f"💼 LinkedIn post: {len(result['linkedin_post'])} characters")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return None


def test_website_url():
    """Test with a website URL"""
    print("\n🧪 Testing website URL extraction...")
    
    # Use a sample website URL
    test_url = "https://example.com"
    
    try:
        result = run_content_repurposing_pipeline(test_url)
        
        print(f"✅ Pipeline completed with status: {result.get('current_step')}")
        print(f"📊 Errors: {len(result.get('errors', []))}")
        
        if result.get('errors'):
            print("❌ Errors found:")
            for error in result.get('errors', []):
                print(f"   - {error}")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return None


def main():
    """Run all tests"""
    print("🚀 Starting EchoWrite AI End-to-End Tests")
    print("=" * 50)
    
    # Test 1: YouTube URL
    youtube_result = test_youtube_url()
    
    # Test 2: Website URL  
    website_result = test_website_url()
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    
    if youtube_result and youtube_result.get('current_step') == 'completed':
        print("✅ YouTube test: PASSED")
    else:
        print("❌ YouTube test: FAILED")
    
    if website_result and website_result.get('current_step') == 'completed':
        print("✅ Website test: PASSED")
    else:
        print("❌ Website test: FAILED")
    
    print("\n🎯 Note: Some failures are expected if dependencies aren't installed yet.")
    print("   Run: pip install -r requirements.txt")
    print("   Make sure your .env file contains GROQ_API_KEY")


if __name__ == "__main__":
    main()