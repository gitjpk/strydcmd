"""Main CLI entry point for strydcmd"""

import argparse
import datetime
import os
import re
import sys
from dotenv import load_dotenv
from strydcmd.stryd_api import StrydAPI


def print_activities(activities, limit: int = None):
    """
    Print activities in a readable format
    
    Args:
        activities: List of activity dictionaries
        limit: Maximum number of activities to display (default: None = all)
    """
    if not activities:
        print("\nNo activities found in the specified time period.")
        return
    
    # Sort by timestamp descending (most recent first)
    sorted_activities = sorted(activities, key=lambda x: x.get('timestamp', 0), reverse=True)
    
    total = len(sorted_activities)
    
    if limit and limit < total:
        display_count = limit
        print(f"\n{'='*80}")
        print(f"Found {total} activities. Displaying the {display_count} most recent:")
        print(f"{'='*80}\n")
        activities_to_show = sorted_activities[:display_count]
    else:
        print(f"\n{'='*80}")
        print(f"Found {total} activities:")
        print(f"{'='*80}\n")
        activities_to_show = sorted_activities
    
    for idx, activity in enumerate(activities_to_show, 1):
        # Parse timestamp
        timestamp = activity.get('timestamp', 0)
        date_str = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        
        # Get activity details
        distance = activity.get('distance', 0) / 1000  # Convert meters to km
        moving_time = activity.get('moving_time', 0) / 60  # Convert seconds to minutes
        avg_power = activity.get('average_power', 0)
        avg_speed = activity.get('average_speed', 0)  # m/s
        avg_hr = activity.get('average_heart_rate', 0)
        activity_type = activity.get('type', 'N/A')
        name = activity.get('name', 'Unnamed Activity')
        
        print(f"Activity #{idx}: {name}")
        print(f"  Date: {date_str}")
        print(f"  Type: {activity_type}")
        print(f"  Distance: {distance:.2f} km")
        print(f"  Moving Time: {moving_time:.1f} minutes")
        
        # Calculate pace from speed
        if avg_speed > 0:
            pace_seconds_per_km = 1000 / avg_speed
            pace_min = int(pace_seconds_per_km / 60)
            pace_sec = int(pace_seconds_per_km % 60)
            print(f"  Avg Pace: {pace_min}:{pace_sec:02d} /km")
        
        if avg_power > 0:
            print(f"  Avg Power: {int(avg_power)} W")
        if avg_hr > 0:
            print(f"  Avg Heart Rate: {int(avg_hr)} bpm")
        
        print()


def main():
    """Main function for Stryd CLI"""
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Stryd API Command Line Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '-g', '--get',
        type=int,
        nargs='?',
        const=30,
        metavar='DAYS',
        help='Get activities from the last N days (default: 30)'
    )
    parser.add_argument(
        '-d', '--date',
        type=str,
        metavar='YYYYMMDD',
        help='Get activities for a specific date (format: YYYYMMDD, e.g., 20260108)'
    )
    parser.add_argument(
        '-t', '--tag',
        type=str,
        metavar='TAG',
        help='Filter activities by tag (e.g., "barcelona 26")'
    )
    parser.add_argument(
        '-f', '--fit',
        action='store_true',
        help='Download FIT files for the retrieved activities'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='fit_files',
        metavar='DIR',
        help='Output directory for FIT files (default: fit_files)'
    )
    
    args = parser.parse_args()
    
    # Validate that -g and -d are mutually exclusive
    if args.get is not None and args.date:
        parser.error("❌ Error: -g/--get and -d/--date options cannot be used together")
    
    # Validate that -t/--tag requires -g/--get
    if args.tag and args.get is None:
        parser.error("❌ Error: -t/--tag option requires -g/--get option")
    
    # Validate that -f/--fit requires either -g/--get or -d/--date
    if args.fit and args.get is None and not args.date:
        parser.error("❌ Error: -f/--fit option requires -g/--get or -d/--date option")
    
    # Validate date format if provided
    if args.date:
        try:
            datetime.datetime.strptime(args.date, "%Y%m%d")
        except ValueError:
            parser.error("❌ Error: Invalid date format. Use YYYYMMDD (e.g., 20260108)")
    
    # Load environment variables from .env file
    load_dotenv()
    
    EMAIL = os.getenv('STRYD_EMAIL')
    PASSWORD = os.getenv('STRYD_PASSWORD')
    
    if not EMAIL or not PASSWORD:
        print("❌ Error: STRYD_EMAIL and STRYD_PASSWORD must be set in .env file")
        print("   Copy .env.example to .env and fill in your credentials")
        return 1
    
    try:
        # Create API client
        stryd = StrydAPI(email=EMAIL, password=PASSWORD)
        
        # If -g/--get option is provided
        if args.get is not None:
            days = args.get
            print(f"Stryd Activities Fetcher")
            print("=" * 80)
            print(f"\nFetching activities from the last {days} days...")
            
            # Authenticate
            stryd.authenticate()
            
            # Get activities
            all_activities = stryd.get_activities(days=days)
            
            # Filter activities to only keep those within the requested time range
            cutoff_timestamp = (datetime.datetime.now() - datetime.timedelta(days=days)).timestamp()
            activities = [a for a in all_activities if a.get('timestamp', 0) >= cutoff_timestamp]
            
            print(f"\nFiltered to {len(activities)} activities from the last {days} days")
            
            # Filter by tag if provided
            if args.tag:
                original_count = len(activities)
                activities = [a for a in activities if args.tag in (a.get('tags') or [])]
                print(f"Filtered by tag '{args.tag}': {len(activities)} activities (from {original_count})")
                
                if len(activities) == 0:
                    # Show available tags to help user
                    all_tags = set()
                    for a in all_activities[:50]:  # Check first 50 activities
                        tags = a.get('tags')
                        if tags:
                            all_tags.update(tags)
                    if all_tags:
                        print(f"\n⚠️  No activities found with tag '{args.tag}'")
                        print(f"\nAvailable tags in recent activities:")
                        for tag in sorted(all_tags):
                            print(f"  - {tag}")
            
            # Print activities (limit display to 20 most recent for readability)
            print_activities(activities, limit=20)
            
            # Download FIT files if requested
            if args.fit:
                print(f"\n{'='*80}")
                print(f"Downloading FIT files to '{args.output}/' directory...")
                print(f"{'='*80}\n")
                
                # Sort activities by timestamp (most recent first)
                sorted_activities = sorted(activities, key=lambda x: x.get('timestamp', 0), reverse=True)
                
                success_count = 0
                fail_count = 0
                
                for idx, activity in enumerate(sorted_activities, 1):
                    activity_id = activity.get('id')
                    activity_name = activity.get('name', 'Unnamed Activity')
                    timestamp = activity.get('timestamp', 0)
                    
                    if not activity_id:
                        continue
                    
                    # Create clean filename: yyyymmdd_activity-name.fit
                    # Get date in yyyymmdd format
                    date_str = datetime.datetime.fromtimestamp(timestamp).strftime("%Y%m%d")
                    # Convert to lowercase, replace spaces with underscores, remove special chars
                    clean_name = re.sub(r'[^a-z0-9_-]', '', activity_name.lower().replace(' ', '_').replace('/', '_'))
                    filename = f"{date_str}_{clean_name}"
                    
                    print(f"[{idx}/{len(sorted_activities)}] Downloading: {activity_name}... ", end='', flush=True)
                    
                    filepath = stryd.download_fit_file(activity_id, args.output, filename=filename)
                    
                    if filepath:
                        print(f"✓ {os.path.basename(filepath)}")
                        success_count += 1
                    else:
                        print(f"✗ Failed")
                        fail_count += 1
                
                print(f"\n{'='*80}")
                print(f"Download complete: {success_count} successful, {fail_count} failed")
                print(f"{'='*80}")
        
        # If -d/--date option is provided
        elif args.date:
            target_date = datetime.datetime.strptime(args.date, "%Y%m%d")
            print(f"Stryd Activities Fetcher")
            print("=" * 80)
            print(f"\nFetching activities for {target_date.strftime('%Y-%m-%d')}...")
            
            # Authenticate
            stryd.authenticate()
            
            # Get activities from a wider range to ensure we get the target day
            all_activities = stryd.get_activities(days=365)
            
            # Filter activities for the specific date
            start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
            end_of_day = target_date.replace(hour=23, minute=59, second=59, microsecond=999999).timestamp()
            activities = [a for a in all_activities if start_of_day <= a.get('timestamp', 0) <= end_of_day]
            
            print(f"\nFound {len(activities)} activities on {target_date.strftime('%Y-%m-%d')}")
            
            # Print activities
            print_activities(activities)
            
            # Download FIT files if requested
            if args.fit:
                if not activities:
                    print(f"\n⚠️  No activities to download for this date")
                else:
                    print(f"\n{'='*80}")
                    print(f"Downloading FIT files to '{args.output}/' directory...")
                    print(f"{'='*80}\n")
                    
                    # Sort activities by timestamp
                    sorted_activities = sorted(activities, key=lambda x: x.get('timestamp', 0), reverse=True)
                    
                    success_count = 0
                    fail_count = 0
                    
                    for idx, activity in enumerate(sorted_activities, 1):
                        activity_id = activity.get('id')
                        activity_name = activity.get('name', 'Unnamed Activity')
                        timestamp = activity.get('timestamp', 0)
                        
                        if not activity_id:
                            continue
                        
                        # Create clean filename: yyyymmdd_activity-name.fit
                        date_str = datetime.datetime.fromtimestamp(timestamp).strftime("%Y%m%d")
                        clean_name = re.sub(r'[^a-z0-9_-]', '', activity_name.lower().replace(' ', '_').replace('/', '_'))
                        filename = f"{date_str}_{clean_name}"
                        
                        print(f"[{idx}/{len(sorted_activities)}] Downloading: {activity_name}... ", end='', flush=True)
                        
                        filepath = stryd.download_fit_file(activity_id, args.output, filename=filename)
                        
                        if filepath:
                            print(f"✓ {os.path.basename(filepath)}")
                            success_count += 1
                        else:
                            print(f"✗ Failed")
                            fail_count += 1
                    
                    print(f"\n{'='*80}")
                    print(f"Download complete: {success_count} successful, {fail_count} failed")
                    print(f"{'='*80}")
        
        else:
            # Default: just test authentication
            print("Stryd API Authentication Test")
            print("=" * 80)
            print("\nAuthenticating...")
            
            token = stryd.authenticate()
            
            print(f"\n✓ Authentication successful!")
            print(f"  Session token: {token[:20]}...")
            if stryd.user_id:
                print(f"  User ID: {stryd.user_id}")
            
            print("\nTip: Use -g or --get to fetch activities (e.g., 'stryd -g 30')")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
