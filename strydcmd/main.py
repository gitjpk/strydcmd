"""Main CLI entry point for strydcmd"""

import argparse
import csv
import datetime
import json
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
        cp = activity.get('ftp', 0)  # Critical Power (FTP)
        activity_type = activity.get('type', 'N/A')
        name = activity.get('name', 'Unnamed Activity')
        
        # Additional details
        rpe = activity.get('rpe', 0)
        feel = activity.get('feel', 'N/A')
        source = activity.get('source', 'N/A')
        surface_type = activity.get('surface_type', 'N/A')
        recording_mode = activity.get('recording_mode', 'N/A')
        critical_impact = activity.get('critical_impact', 0)
        elevation_gain = activity.get('total_elevation_gain', 0)
        elevation_loss = activity.get('total_elevation_loss', 0)
        tags = activity.get('tags', [])
        
        print(f"Activity #{idx}: {name}")
        print(f"  Date: {date_str}")
        print(f"  Type: {activity_type}")
        if feel != 'N/A':
            print(f"  Feel: {feel}")
        if rpe > 0:
            print(f"  RPE: {rpe}/10")
        if source != 'N/A':
            print(f"  Source: {source}")
        if surface_type != 'N/A':
            print(f"  Surface: {surface_type}")
        if recording_mode != 'N/A':
            print(f"  Recording Mode: {recording_mode}")
        if tags:
            print(f"  Tags: {', '.join(tags)}")
        print(f"  Distance: {distance:.2f} km")
        print(f"  Moving Time: {moving_time:.1f} minutes")
        if elevation_gain != 0:
            print(f"  Elevation Gain: {elevation_gain:.1f} m")
        if elevation_loss != 0:
            print(f"  Elevation Loss: {abs(elevation_loss):.1f} m")
        
        # Calculate pace from speed
        if avg_speed > 0:
            pace_seconds_per_km = 1000 / avg_speed
            pace_min = int(pace_seconds_per_km / 60)
            pace_sec = int(pace_seconds_per_km % 60)
            print(f"  Avg Pace: {pace_min}:{pace_sec:02d} /km")
        
        if avg_power > 0:
            print(f"  Avg Power: {int(avg_power)} W")
        if cp > 0:
            print(f"  Critical Power: {int(cp)} W")
        if critical_impact != 0:
            print(f"  Critical Impact: {critical_impact:.1f}")
        if avg_hr > 0:
            print(f"  Avg Heart Rate: {int(avg_hr)} bpm")
        
        # Power zones analysis
        zones = activity.get('zones', [])
        seconds_in_zones = activity.get('seconds_in_zones', [])
        if zones and seconds_in_zones and len(zones) == len(seconds_in_zones):
            print(f"\n  Power Zones:")
            for zone, seconds in zip(zones, seconds_in_zones):
                if moving_time > 0:
                    pct = (seconds / (moving_time * 60)) * 100  # moving_time is in minutes
                    minutes = seconds / 60
                    zone_name = zone.get('name', 'Unknown')
                    power_low = int(zone.get('power_low', 0))
                    power_high = int(zone.get('power_high', 0))
                    print(f"    {zone_name} ({power_low}-{power_high}W): {minutes:.1f}min ({pct:.1f}%)")
        
        print()


def export_activities_csv(activities, filename):
    """
    Export activities to CSV file
    
    Args:
        activities: List of activity dictionaries
        filename: Output CSV filename
    """
    if not activities:
        print("No activities to export.")
        return
    
    # Define CSV columns
    fieldnames = [
        'date', 'name', 'type', 'feel', 'rpe', 'source', 'surface_type', 
        'recording_mode', 'tags', 'distance_km', 'moving_time_min', 
        'elevation_gain_m', 'elevation_loss_m', 'avg_pace_min_km', 
        'avg_power_w', 'critical_power_w', 'critical_impact', 'avg_heart_rate_bpm',
        'zone_easy_min', 'zone_easy_pct', 'zone_moderate_min', 'zone_moderate_pct',
        'zone_threshold_min', 'zone_threshold_pct', 'zone_interval_min', 'zone_interval_pct',
        'zone_repetition_min', 'zone_repetition_pct'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for activity in activities:
            timestamp = activity.get('timestamp', 0)
            date_str = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
            distance = activity.get('distance', 0) / 1000
            moving_time = activity.get('moving_time', 0) / 60
            avg_speed = activity.get('average_speed', 0)
            
            # Calculate pace
            avg_pace = ""
            if avg_speed > 0:
                pace_seconds_per_km = 1000 / avg_speed
                pace_min = int(pace_seconds_per_km / 60)
                pace_sec = int(pace_seconds_per_km % 60)
                avg_pace = f"{pace_min}:{pace_sec:02d}"
            
            tags = activity.get('tags', [])
            tags_str = ', '.join(tags) if tags else ''
            
            # Calculate power zones
            zones = activity.get('zones', [])
            seconds_in_zones = activity.get('seconds_in_zones', [])
            zone_data = {}
            if zones and seconds_in_zones and len(zones) == len(seconds_in_zones):
                zone_names = ['easy', 'moderate', 'threshold', 'interval', 'repetition']
                for i, (zone, seconds) in enumerate(zip(zones, seconds_in_zones)):
                    if i < len(zone_names):
                        minutes = seconds / 60
                        pct = (seconds / (moving_time * 60)) * 100 if moving_time > 0 else 0
                        zone_data[f'zone_{zone_names[i]}_min'] = f"{minutes:.1f}"
                        zone_data[f'zone_{zone_names[i]}_pct'] = f"{pct:.1f}"
            
            # Fill missing zones with 0
            for zone_name in ['easy', 'moderate', 'threshold', 'interval', 'repetition']:
                if f'zone_{zone_name}_min' not in zone_data:
                    zone_data[f'zone_{zone_name}_min'] = "0.0"
                    zone_data[f'zone_{zone_name}_pct'] = "0.0"
            
            row = {
                'date': date_str,
                'name': activity.get('name', ''),
                'type': activity.get('type', ''),
                'feel': activity.get('feel', ''),
                'rpe': activity.get('rpe', ''),
                'source': activity.get('source', ''),
                'surface_type': activity.get('surface_type', ''),
                'recording_mode': activity.get('recording_mode', ''),
                'tags': tags_str,
                'distance_km': f"{distance:.2f}",
                'moving_time_min': f"{moving_time:.1f}",
                'elevation_gain_m': f"{activity.get('total_elevation_gain', 0):.1f}",
                'elevation_loss_m': f"{abs(activity.get('total_elevation_loss', 0)):.1f}",
                'avg_pace_min_km': avg_pace,
                'avg_power_w': int(activity.get('average_power', 0)),
                'critical_power_w': int(activity.get('ftp', 0)),
                'critical_impact': f"{activity.get('critical_impact', 0):.1f}",
                'avg_heart_rate_bpm': int(activity.get('average_heart_rate', 0)),
                **zone_data
            }
            writer.writerow(row)
    
    print(f"\n✓ Exported {len(activities)} activities to {filename}")


def export_activities_json(activities, filename):
    """
    Export activities to JSON file
    
    Args:
        activities: List of activity dictionaries
        filename: Output JSON filename
    """
    if not activities:
        print("No activities to export.")
        return
    
    # Prepare simplified activity data for JSON
    export_data = []
    for activity in activities:
        timestamp = activity.get('timestamp', 0)
        date_str = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        distance = activity.get('distance', 0) / 1000
        moving_time = activity.get('moving_time', 0) / 60
        avg_speed = activity.get('average_speed', 0)
        
        # Calculate pace
        avg_pace = ""
        if avg_speed > 0:
            pace_seconds_per_km = 1000 / avg_speed
            pace_min = int(pace_seconds_per_km / 60)
            pace_sec = int(pace_seconds_per_km % 60)
            avg_pace = f"{pace_min}:{pace_sec:02d}"
        
        # Calculate power zones
        zones = activity.get('zones', [])
        seconds_in_zones = activity.get('seconds_in_zones', [])
        power_zones = []
        if zones and seconds_in_zones and len(zones) == len(seconds_in_zones):
            for zone, seconds in zip(zones, seconds_in_zones):
                minutes = seconds / 60
                pct = (seconds / (moving_time * 60)) * 100 if moving_time > 0 else 0
                power_zones.append({
                    'name': zone.get('name', 'Unknown'),
                    'power_low': int(zone.get('power_low', 0)),
                    'power_high': int(zone.get('power_high', 0)),
                    'time_min': round(minutes, 1),
                    'time_pct': round(pct, 1)
                })
        
        activity_data = {
            'date': date_str,
            'name': activity.get('name', ''),
            'type': activity.get('type', ''),
            'feel': activity.get('feel', ''),
            'rpe': activity.get('rpe', 0),
            'source': activity.get('source', ''),
            'surface_type': activity.get('surface_type', ''),
            'recording_mode': activity.get('recording_mode', ''),
            'tags': activity.get('tags', []),
            'distance_km': round(distance, 2),
            'moving_time_min': round(moving_time, 1),
            'elevation_gain_m': round(activity.get('total_elevation_gain', 0), 1),
            'elevation_loss_m': round(abs(activity.get('total_elevation_loss', 0)), 1),
            'avg_pace_min_km': avg_pace,
            'avg_power_w': int(activity.get('average_power', 0)),
            'critical_power_w': int(activity.get('ftp', 0)),
            'critical_impact': round(activity.get('critical_impact', 0), 1),
            'avg_heart_rate_bpm': int(activity.get('average_heart_rate', 0)),
            'power_zones': power_zones
        }
        export_data.append(activity_data)
    
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Exported {len(activities)} activities to {filename}")


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
    parser.add_argument(
        '-e', '--export',
        nargs='*',
        metavar=('FORMAT', 'FILE'),
        help='Export activities to CSV or JSON (default: CSV stryd_export.csv). Usage: -e CSV file.csv or -e JSON file.json or -e file.csv'
    )
    
    args = parser.parse_args()
    
    # Parse export arguments
    export_format = None
    export_filename = None
    if args.export is not None:
        if len(args.export) == 0:
            # -e without arguments: use defaults
            export_format = 'CSV'
            export_filename = 'stryd_export.csv'
        elif len(args.export) == 1:
            # -e with one argument: could be format or filename
            arg = args.export[0].upper()
            if arg in ['CSV', 'JSON']:
                export_format = arg
                export_filename = f'stryd_export.{arg.lower()}'
            else:
                # It's a filename, determine format from extension or use default
                export_filename = args.export[0]
                if export_filename.lower().endswith('.json'):
                    export_format = 'JSON'
                else:
                    export_format = 'CSV'
                    if not export_filename.lower().endswith('.csv'):
                        export_filename += '.csv'
        elif len(args.export) == 2:
            # -e with two arguments: format and filename
            export_format = args.export[0].upper()
            export_filename = args.export[1]
            if export_format not in ['CSV', 'JSON']:
                parser.error("❌ Error: Export format must be CSV or JSON")
            # Add extension if not present
            expected_ext = f'.{export_format.lower()}'
            if not export_filename.lower().endswith(expected_ext):
                export_filename += expected_ext
        else:
            parser.error("❌ Error: -e/--export accepts 0, 1, or 2 arguments")
    
    # Validate that -e/--export requires either -g/--get or -d/--date
    if args.export is not None and args.get is None and not args.date:
        parser.error("❌ Error: -e/--export option requires -g/--get or -d/--date option")
    
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
            
            # Export activities if requested
            if export_format and export_filename:
                if export_format == 'CSV':
                    export_activities_csv(activities, export_filename)
                elif export_format == 'JSON':
                    export_activities_json(activities, export_filename)
            
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
            
            # Export activities if requested
            if export_format and export_filename:
                if export_format == 'CSV':
                    export_activities_csv(activities, export_filename)
                elif export_format == 'JSON':
                    export_activities_json(activities, export_filename)
            
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
