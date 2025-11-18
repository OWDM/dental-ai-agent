"""
Test Supabase Database Connection
This script tests the connection to your Supabase database and verifies the schema.
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection():
    """Test connection to Supabase"""
    print("=" * 60)
    print("🧪 Testing Supabase Database Connection")
    print("=" * 60)

    # Get credentials from environment
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        print("❌ Error: Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env file")
        return False

    print(f"\n📍 Supabase URL: {url}")
    print(f"🔑 Using Service Role Key: {key[:20]}...")

    try:
        # Create Supabase client
        print("\n⏳ Connecting to Supabase...")
        supabase: Client = create_client(url, key)
        print("✅ Connection successful!")

        # Test 1: Check Patients table
        print("\n" + "=" * 60)
        print("Test 1: Fetching Patients")
        print("=" * 60)
        response = supabase.table("patients").select("*").execute()
        print(f"✅ Found {len(response.data)} patients")
        if response.data:
            print(f"   Sample patient: {response.data[0]['name']} ({response.data[0]['email']})")

        # Test 2: Check Doctors table
        print("\n" + "=" * 60)
        print("Test 2: Fetching Doctors")
        print("=" * 60)
        response = supabase.table("doctors").select("*").execute()
        print(f"✅ Found {len(response.data)} doctors")
        if response.data:
            print(f"   Sample doctor: {response.data[0]['name']} - {response.data[0]['specialization']}")

        # Test 3: Check Services table
        print("\n" + "=" * 60)
        print("Test 3: Fetching Services")
        print("=" * 60)
        response = supabase.table("services").select("*").execute()
        print(f"✅ Found {len(response.data)} services")
        if response.data:
            print(f"   Sample service: {response.data[0]['name']} - {response.data[0]['price']} SAR")

        # Test 4: Check Support Tickets table
        print("\n" + "=" * 60)
        print("Test 4: Fetching Support Tickets")
        print("=" * 60)
        response = supabase.table("support_tickets").select("*").execute()
        print(f"✅ Found {len(response.data)} support tickets")
        if response.data:
            ticket = response.data[0]
            print(f"   Sample ticket: {ticket['subject']}")
            print(f"   Type: {ticket.get('type', 'N/A')}")
            print(f"   Status: {ticket['status']}")
            if ticket.get('conversation_history'):
                messages = ticket['conversation_history'].get('messages', [])
                print(f"   Messages: {len(messages)}")

        # Test 5: Check Feedback table
        print("\n" + "=" * 60)
        print("Test 5: Fetching Feedback")
        print("=" * 60)
        response = supabase.table("feedback").select("*").execute()
        print(f"✅ Found {len(response.data)} feedback entries")
        if response.data:
            feedback = response.data[0]
            print(f"   Sample feedback: {feedback['feedback_type']} - {feedback['category']}")

        # Summary
        print("\n" + "=" * 60)
        print("✅ All Tests Passed!")
        print("=" * 60)
        print("📊 Database Summary:")
        print(f"   • Patients: Ready")
        print(f"   • Doctors: Ready")
        print(f"   • Services: Ready")
        print(f"   • Support Tickets: Ready")
        print(f"   • Feedback: Ready")
        print("\n🎉 Your Supabase database is ready to use!")

        return True

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\n💡 Troubleshooting:")
        print("   1. Check that you ran schema.sql and mock_data.sql in Supabase")
        print("   2. Verify your credentials in the .env file")
        print("   3. Ensure your IP is allowed in Supabase settings")
        return False

if __name__ == "__main__":
    test_connection()