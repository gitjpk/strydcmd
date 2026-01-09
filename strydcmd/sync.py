"""Stryd Activity Sync Command - Synchronize activities to SQLite database"""

import argparse
import datetime
import os
import sys
from typing import List, Dict
from dotenv import load_dotenv

from .stryd_api import StrydAPI
from .database import StrydDatabase


def filter_activities_by_date(activities: List[Dict], days: int = None, date_str: str = None) -> List[Dict]:
    """
    Filter activities by days or specific date
    
    Args:
        activities: List of activity dictionaries
        days: Number of days to look back from now
        date_str: Specific date in YYYYMMDD format
        
    Returns:
        Filtered list of activities
    """
    if date_str:
        # Parse specific date
        try:
            target_date = datetime.datetime.strptime(date_str, "%Y%m%d")
            start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            start_timestamp = start_of_day.timestamp()
            end_timestamp = end_of_day.timestamp()
            
            filtered = [
                a for a in activities 
                if start_timestamp <= a.get('timestamp', 0) <= end_timestamp
            ]
            
            print(f"Filtering activities for date: {target_date.strftime('%Y-%m-%d')}")
            return filtered
            
        except ValueError:
            print(f"✗ Invalid date format: {date_str}. Use YYYYMMDD")
            return []
    
    elif days:
        # Filter by last N days
        now = datetime.datetime.now()
        cutoff = now - datetime.timedelta(days=days)
        cutoff_timestamp = cutoff.timestamp()
        
        filtered = [
            a for a in activities 
            if a.get('timestamp', 0) >= cutoff_timestamp
        ]
        
        print(f"Filtering activities from last {days} days")
        return filtered
    
    else:
        # No filter, return all
        return activities


def sync_activities(api: StrydAPI, db: StrydDatabase, activities: List[Dict], 
                   force: bool = False, batch_size: int = 10):
    """
    Synchronize activities to database with pagination
    
    Args:
        api: Authenticated StrydAPI client
        db: StrydDatabase instance
        activities: List of activity summaries from calendar
        force: If True, overwrite existing activities
        batch_size: Number of activities to process per batch
    """
    total = len(activities)
    synced_count = 0
    skipped_count = 0
    failed_count = 0
    
    print(f"\n{'='*60}")
    print(f"Starting sync: {total} activities to process")
    print(f"Batch size: {batch_size} activities")
    print(f"Force mode: {'ON' if force else 'OFF'}")
    print(f"{'='*60}\n")
    
    # Process in batches
    for batch_start in range(0, total, batch_size):
        batch_end = min(batch_start + batch_size, total)
        batch_num = (batch_start // batch_size) + 1
        total_batches = (total + batch_size - 1) // batch_size
        
        print(f"\n--- Batch {batch_num}/{total_batches} (activities {batch_start + 1}-{batch_end}) ---")
        
        for i in range(batch_start, batch_end):
            activity = activities[i]
            activity_id = activity.get('id')
            activity_name = activity.get('name', 'Unnamed Activity')
            activity_date = datetime.datetime.fromtimestamp(
                activity.get('timestamp', 0)
            ).strftime('%Y-%m-%d')
            
            # Progress indicator
            progress = f"[{i + 1}/{total}]"
            
            # Check if activity already exists
            if db.activity_exists(activity_id) and not force:
                print(f"  {progress} ✓ {activity_name} ({activity_date}) - already synced, skipping")
                skipped_count += 1
                continue
            
            # Fetch detailed activity data
            print(f"  {progress} → Fetching details for {activity_name} ({activity_date})...")
            activity_details = api.get_activity_details(activity_id)
            
            if not activity_details:
                print(f"  {progress} ✗ Failed to fetch details for {activity_name}")
                failed_count += 1
                continue
            
            # Save to database
            success, message = db.save_activity(activity_details, force=force)
            
            if success:
                action = "updated" if force and db.activity_exists(activity_id) else "saved"
                print(f"  {progress} ✓ {activity_name} ({activity_date}) - {action}")
                synced_count += 1
            else:
                print(f"  {progress} ✗ {activity_name} ({activity_date}) - {message}")
                failed_count += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Sync completed!")
    print(f"  • New/Updated: {synced_count}")
    print(f"  • Skipped:     {skipped_count}")
    print(f"  • Failed:      {failed_count}")
    print(f"  • Total in DB: {db.get_activity_count()}")
    print(f"{'='*60}\n")


def main():
    """Main entry point for strydsync command"""
    
    parser = argparse.ArgumentParser(
        description='Synchronize Stryd activities to SQLite database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  strydsync              # Sync last 30 days
  strydsync 60           # Sync last 60 days
  strydsync -d 20260108  # Sync specific date
  strydsync --force      # Resync all activities from last 30 days
  strydsync 90 --force   # Resync all activities from last 90 days
        """
    )
    
    parser.add_argument(
        'days',
        type=int,
        nargs='?',
        default=30,
        help='Number of days to sync (default: 30)'
    )
    
    parser.add_argument(
        '-d', '--date',
        type=str,
        help='Sync specific date (format: YYYYMMDD)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force resynchronization of existing activities'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=10,
        help='Number of activities per batch (default: 10)'
    )
    
    parser.add_argument(
        '--db',
        type=str,
        default='stryd_activities.db',
        help='Database file path (default: stryd_activities.db)'
    )
    
    args = parser.parse_args()
    
    # Validate: days and -d are mutually exclusive
    if args.date and args.days != 30:
        print("✗ Error: Cannot use both days argument and -d/--date option")
        sys.exit(1)
    
    # Load environment variables
    load_dotenv()
    
    email = os.getenv('STRYD_EMAIL')
    password = os.getenv('STRYD_PASSWORD')
    
    if not email or not password:
        print("✗ Error: STRYD_EMAIL and STRYD_PASSWORD must be set in .env file")
        print("\nCreate a .env file with:")
        print("  STRYD_EMAIL=your.email@example.com")
        print("  STRYD_PASSWORD=your_password")
        sys.exit(1)
    
    try:
        # Initialize API
        print("Initializing Stryd API...")
        api = StrydAPI(email, password)
        api.authenticate()
        
        # Initialize database
        print(f"Opening database: {args.db}")
        db = StrydDatabase(db_path=args.db)
        db.connect()
        
        # Get activities from calendar
        # Note: API returns all activities, we'll filter them
        if args.date:
            # For specific date, get a week around it to ensure we have the data
            fetch_days = 7
        else:
            fetch_days = args.days
        
        print(f"\nFetching activities...")
        all_activities = api.get_activities(days=fetch_days * 2)  # Fetch extra to be safe
        
        if not all_activities:
            print("✗ No activities found")
            db.close()
            return
        
        # Filter activities
        filtered_activities = filter_activities_by_date(
            all_activities,
            days=args.days if not args.date else None,
            date_str=args.date
        )
        
        if not filtered_activities:
            print("✗ No activities found matching the specified criteria")
            db.close()
            return
        
        print(f"Found {len(filtered_activities)} activities to sync")
        
        # Sort by date (oldest first)
        filtered_activities.sort(key=lambda a: a.get('timestamp', 0))
        
        # Sync activities
        sync_activities(
            api=api,
            db=db,
            activities=filtered_activities,
            force=args.force,
            batch_size=args.batch_size
        )
        
        # Close database
        db.close()
        print(f"Database closed: {args.db}")
        
    except KeyboardInterrupt:
        print("\n\n✗ Sync interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
