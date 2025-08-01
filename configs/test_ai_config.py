#!/usr/bin/env python3
"""
Test script for AI API configuration.
Run this script to verify that your API keys are properly configured.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from configs.ai_config import ai_config


def test_configuration():
    """Test AI configuration setup."""
    print("🔍 Testing AI API Configuration...")
    print("=" * 50)
    
    # Test environment variables
    print("📋 Environment Variables:")
    print(f"  OPENAI_API_KEY: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Not set'}")
    print(f"  ANTHROPIC_API_KEY: {'✅ Set' if os.getenv('ANTHROPIC_API_KEY') else '❌ Not set'}")
    print()
    
    # Test configuration object
    print("⚙️  Configuration Object:")
    print(f"  OpenAI API Key: {'✅ Configured' if ai_config.openai_api_key else '❌ Not configured'}")
    print(f"  OpenAI Model: {ai_config.openai_model}")
    print(f"  Anthropic API Key: {'✅ Configured' if ai_config.anthropic_api_key else '❌ Not configured'}")
    print(f"  Anthropic Model: {ai_config.anthropic_model}")
    print()
    
    # Validate configuration
    print("🔐 Validation:")
    is_valid = ai_config.validate_config()
    if is_valid:
        print("  ✅ Configuration is valid")
    else:
        print("  ❌ Configuration is invalid - please set API keys")
    print()
    
    # Show configuration details
    if ai_config.openai_api_key:
        print("📤 OpenAI Configuration:")
        openai_config = ai_config.get_openai_config()
        for key, value in openai_config.items():
            if key == 'api_key':
                # Mask API key for security
                masked_key = value[:8] + "..." + value[-4:] if value else "Not set"
                print(f"    {key}: {masked_key}")
            else:
                print(f"    {key}: {value}")
        print()
    
    if ai_config.anthropic_api_key:
        print("📤 Anthropic Configuration:")
        anthropic_config = ai_config.get_anthropic_config()
        for key, value in anthropic_config.items():
            if key == 'api_key':
                # Mask API key for security
                masked_key = value[:8] + "..." + value[-4:] if value else "Not set"
                print(f"    {key}: {masked_key}")
            else:
                print(f"    {key}: {value}")
        print()
    
    return is_valid


def main():
    """Main function."""
    print("🚀 AI API Configuration Test")
    print("=" * 50)
    
    try:
        is_valid = test_configuration()
        
        if is_valid:
            print("✅ Configuration test completed successfully!")
            print("\n📝 Next steps:")
            print("  1. Install required packages: pip install openai anthropic")
            print("  2. Test API connections with actual requests")
            print("  3. Start using AI services in your application")
        else:
            print("❌ Configuration test failed!")
            print("\n📝 To fix:")
            print("  1. Create .env file: cp env.example .env")
            print("  2. Add your API keys to .env file")
            print("  3. Run this test again")
        
    except Exception as e:
        print(f"❌ Error during configuration test: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 