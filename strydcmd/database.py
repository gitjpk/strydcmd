"""SQLite database management for Stryd activities"""

import sqlite3
import os
from typing import Optional, List, Dict, Any
import json


class StrydDatabase:
    """Manage SQLite database for Stryd activities"""
    
    def __init__(self, db_path: str = "stryd_activities.db"):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Connect to database and create tables if needed"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
        
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            
    def _create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Main activities table (metadata)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY,
                user_id TEXT,
                name TEXT,
                description TEXT,
                type TEXT,
                feel TEXT,
                rpe INTEGER,
                timestamp INTEGER,
                start_time INTEGER,
                date TEXT,
                moving_time INTEGER,
                elapsed_time INTEGER,
                clock_time INTEGER,
                time_zone TEXT,
                distance REAL,
                total_elevation_gain REAL,
                total_elevation_loss REAL,
                min_elevation REAL,
                max_elevation REAL,
                average_speed REAL,
                max_speed REAL,
                average_cadence INTEGER,
                min_cadence INTEGER,
                max_cadence INTEGER,
                average_stride_length REAL,
                min_stride_length REAL,
                max_stride_length REAL,
                average_power REAL,
                max_power INTEGER,
                ftp REAL,
                critical_impact REAL,
                average_heart_rate INTEGER,
                max_heart_rate INTEGER,
                calories INTEGER,
                average_ground_time REAL,
                min_ground_time INTEGER,
                max_ground_time INTEGER,
                average_ground_time_balance REAL,
                average_oscillation REAL,
                min_oscillation REAL,
                max_oscillation REAL,
                average_vertical_ratio REAL,
                average_vertical_oscillation_balance REAL,
                average_leg_spring REAL,
                average_leg_spring_stiffness_balance REAL,
                average_impact_loading_rate_balance REAL,
                max_vertical_stiffness REAL,
                stress REAL,
                lower_body_stress REAL,
                stryds REAL,
                source TEXT,
                surface_type TEXT,
                recording_mode TEXT,
                sport_type INTEGER,
                power_type TEXT,
                weight INTEGER,
                height INTEGER,
                temperature INTEGER,
                dewPoint INTEGER,
                humidity INTEGER,
                windSpeed REAL,
                windBearing INTEGER,
                windGust INTEGER,
                icon TEXT,
                location_city TEXT,
                location_country TEXT,
                location_state TEXT,
                tags TEXT,
                workout_id TEXT,
                workout_source TEXT,
                workout_source_id TEXT,
                file_path TEXT,
                map_image_link TEXT,
                polyline TEXT,
                summary_polyline TEXT,
                start_lat REAL,
                start_lng REAL,
                end_lat REAL,
                end_lng REAL,
                device_id TEXT,
                device_model TEXT,
                device_sw_rev TEXT,
                device_fw_rev TEXT,
                watch_product_id TEXT,
                watch_manufacturer TEXT,
                created INTEGER,
                updated INTEGER,
                synced_at INTEGER,
                UNIQUE(id)
            )
        """)
        
        # Power zones distribution
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS zones_distribution (
                activity_id INTEGER,
                zone_name TEXT,
                power_low INTEGER,
                power_high INTEGER,
                seconds INTEGER,
                percentage REAL,
                FOREIGN KEY (activity_id) REFERENCES activities(id),
                PRIMARY KEY (activity_id, zone_name)
            )
        """)
        
        # Time series: Power
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS timeseries_power (
                activity_id INTEGER,
                timestamp INTEGER,
                total_power INTEGER,
                horizontal_power INTEGER,
                vertical_power INTEGER,
                air_power INTEGER,
                elevation_power REAL,
                FOREIGN KEY (activity_id) REFERENCES activities(id)
            )
        """)
        
        # Time series: Kinematics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS timeseries_kinematics (
                activity_id INTEGER,
                timestamp INTEGER,
                speed REAL,
                distance REAL,
                cadence INTEGER,
                stride_length REAL,
                FOREIGN KEY (activity_id) REFERENCES activities(id)
            )
        """)
        
        # Time series: Cardio
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS timeseries_cardio (
                activity_id INTEGER,
                timestamp INTEGER,
                heart_rate INTEGER,
                rr_interval INTEGER,
                FOREIGN KEY (activity_id) REFERENCES activities(id)
            )
        """)
        
        # Time series: Biomechanics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS timeseries_biomechanics (
                activity_id INTEGER,
                timestamp INTEGER,
                ground_time INTEGER,
                ground_time_balance REAL,
                oscillation REAL,
                vertical_oscillation_balance REAL,
                leg_spring INTEGER,
                leg_spring_stiffness_balance REAL,
                impact INTEGER,
                impact_loading_rate_balance REAL,
                vertical_ratio REAL,
                FOREIGN KEY (activity_id) REFERENCES activities(id)
            )
        """)
        
        # Time series: Elevation
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS timeseries_elevation (
                activity_id INTEGER,
                timestamp INTEGER,
                elevation REAL,
                grade INTEGER,
                FOREIGN KEY (activity_id) REFERENCES activities(id)
            )
        """)
        
        # GPS points
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gps_points (
                activity_id INTEGER,
                timestamp INTEGER,
                lat REAL,
                lng REAL,
                FOREIGN KEY (activity_id) REFERENCES activities(id)
            )
        """)
        
        # Laps
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS laps (
                activity_id INTEGER,
                lap_number INTEGER,
                timestamp INTEGER,
                trigger INTEGER,
                workout_step INTEGER,
                FOREIGN KEY (activity_id) REFERENCES activities(id),
                PRIMARY KEY (activity_id, lap_number)
            )
        """)
        
        # Create indexes for better query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_date ON activities(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_type ON activities(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_timestamp ON activities(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timeseries_power_activity ON timeseries_power(activity_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timeseries_kinematics_activity ON timeseries_kinematics(activity_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timeseries_cardio_activity ON timeseries_cardio(activity_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timeseries_biomechanics_activity ON timeseries_biomechanics(activity_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_gps_points_activity ON gps_points(activity_id)")
        
        self.conn.commit()
        
    def activity_exists(self, activity_id: int) -> bool:
        """
        Check if activity already exists in database
        
        Args:
            activity_id: Activity ID
            
        Returns:
            True if activity exists, False otherwise
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM activities WHERE id = ?", (activity_id,))
        count = cursor.fetchone()[0]
        return count > 0
    
    def save_activity(self, activity_data: Dict[str, Any], force: bool = False):
        """
        Save activity data to database
        
        Args:
            activity_data: Complete activity data from Stryd API
            force: If True, overwrite existing data
        """
        activity_id = activity_data.get('id')
        
        # Check if exists
        if self.activity_exists(activity_id) and not force:
            return False, "Activity already exists"
        
        cursor = self.conn.cursor()
        
        # Delete existing if force mode
        if force and self.activity_exists(activity_id):
            cursor.execute("DELETE FROM activities WHERE id = ?", (activity_id,))
            cursor.execute("DELETE FROM zones_distribution WHERE activity_id = ?", (activity_id,))
            cursor.execute("DELETE FROM timeseries_power WHERE activity_id = ?", (activity_id,))
            cursor.execute("DELETE FROM timeseries_kinematics WHERE activity_id = ?", (activity_id,))
            cursor.execute("DELETE FROM timeseries_cardio WHERE activity_id = ?", (activity_id,))
            cursor.execute("DELETE FROM timeseries_biomechanics WHERE activity_id = ?", (activity_id,))
            cursor.execute("DELETE FROM timeseries_elevation WHERE activity_id = ?", (activity_id,))
            cursor.execute("DELETE FROM gps_points WHERE activity_id = ?", (activity_id,))
            cursor.execute("DELETE FROM laps WHERE activity_id = ?", (activity_id,))
        
        # Insert activity metadata
        import datetime
        timestamp = activity_data.get('timestamp', 0)
        date_str = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        
        tags = activity_data.get('tags', [])
        tags_str = ','.join(tags) if tags else ''
        
        start_point = activity_data.get('start_point', {})
        end_point = activity_data.get('end_point', {})
        map_data = activity_data.get('map', {})
        device_info = activity_data.get('device_info', {})
        watch_info = activity_data.get('watch_info', {})
        
        cursor.execute("""
            INSERT INTO activities VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        """, (
            activity_id,
            activity_data.get('user_id'),
            activity_data.get('name'),
            activity_data.get('description'),
            activity_data.get('type'),
            activity_data.get('feel'),
            activity_data.get('rpe'),
            timestamp,
            activity_data.get('start_time'),
            date_str,
            activity_data.get('moving_time'),
            activity_data.get('elapsed_time'),
            activity_data.get('clock_time'),
            activity_data.get('time_zone'),
            activity_data.get('distance'),
            activity_data.get('total_elevation_gain'),
            activity_data.get('total_elevation_loss'),
            activity_data.get('min_elevation'),
            activity_data.get('max_elevation'),
            activity_data.get('average_speed'),
            activity_data.get('max_speed'),
            activity_data.get('average_cadence'),
            activity_data.get('min_cadence'),
            activity_data.get('max_cadence'),
            activity_data.get('average_stride_length'),
            activity_data.get('min_stride_length'),
            activity_data.get('max_stride_length'),
            activity_data.get('average_power'),
            activity_data.get('max_power'),
            activity_data.get('ftp'),
            activity_data.get('critical_impact'),
            activity_data.get('average_heart_rate'),
            activity_data.get('max_heart_rate'),
            activity_data.get('calories'),
            activity_data.get('average_ground_time'),
            activity_data.get('min_ground_time'),
            activity_data.get('max_ground_time'),
            activity_data.get('average_ground_time_balance'),
            activity_data.get('average_oscillation'),
            activity_data.get('min_oscillation'),
            activity_data.get('max_oscillation'),
            activity_data.get('average_vertical_ratio'),
            activity_data.get('average_vertical_oscillation_balance'),
            activity_data.get('average_leg_spring'),
            activity_data.get('average_leg_spring_stiffness_balance'),
            activity_data.get('average_impact_loading_rate_balance'),
            activity_data.get('max_vertical_stiffness'),
            activity_data.get('stress'),
            activity_data.get('lower_body_stress'),
            activity_data.get('stryds'),
            activity_data.get('source'),
            activity_data.get('surface_type'),
            activity_data.get('recording_mode'),
            activity_data.get('sport_type'),
            activity_data.get('power_type'),
            activity_data.get('weight'),
            activity_data.get('height'),
            activity_data.get('temperature'),
            activity_data.get('dewPoint'),
            activity_data.get('humidity'),
            activity_data.get('windSpeed'),
            activity_data.get('windBearing'),
            activity_data.get('windGust'),
            activity_data.get('icon'),
            activity_data.get('location_city'),
            activity_data.get('location_country'),
            activity_data.get('location_state'),
            tags_str,
            activity_data.get('workout_id'),
            activity_data.get('workout_source'),
            activity_data.get('workout_source_id'),
            activity_data.get('file_path'),
            activity_data.get('map_image_link'),
            map_data.get('polyline'),
            map_data.get('summary_polyline'),
            start_point.get('Lat'),
            start_point.get('Lng'),
            end_point.get('Lat'),
            end_point.get('Lng'),
            device_info.get('device_id'),
            device_info.get('device_model'),
            device_info.get('device_sw_rev'),
            device_info.get('device_fw_rev'),
            watch_info.get('product_id'),
            watch_info.get('manufacturer'),
            activity_data.get('created'),
            activity_data.get('updated'),
            int(datetime.datetime.now().timestamp())
        ))
        
        # Save zones
        zones = activity_data.get('zones', [])
        seconds_in_zones = activity_data.get('seconds_in_zones', [])
        moving_time = activity_data.get('moving_time', 0)
        
        for zone, seconds in zip(zones, seconds_in_zones):
            pct = (seconds / moving_time * 100) if moving_time > 0 else 0
            cursor.execute("""
                INSERT INTO zones_distribution VALUES (?, ?, ?, ?, ?, ?)
            """, (
                activity_id,
                zone.get('name'),
                int(zone.get('power_low', 0)),
                int(zone.get('power_high', 0)),
                seconds,
                pct
            ))
        
        # Save time series data
        timestamp_list = activity_data.get('timestamp_list') or []
        if timestamp_list:
            # Power
            total_power_list = activity_data.get('total_power_list') or []
            horizontal_power_list = activity_data.get('horizontal_power_list') or []
            vertical_power_list = activity_data.get('vertical_power_list') or []
            air_power_list = activity_data.get('air_power_list') or []
            elevation_power_list = activity_data.get('elevation_power_list') or []
            
            for i, ts in enumerate(timestamp_list):
                cursor.execute("""
                    INSERT INTO timeseries_power VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    activity_id, ts,
                    total_power_list[i] if i < len(total_power_list) else None,
                    horizontal_power_list[i] if i < len(horizontal_power_list) else None,
                    vertical_power_list[i] if i < len(vertical_power_list) else None,
                    air_power_list[i] if i < len(air_power_list) else None,
                    elevation_power_list[i] if i < len(elevation_power_list) else None
                ))
            
            # Kinematics
            speed_list = activity_data.get('speed_list') or []
            distance_list = activity_data.get('distance_list') or []
            cadence_list = activity_data.get('cadence_list') or []
            stride_length_list = activity_data.get('stride_length_list') or []
            
            for i, ts in enumerate(timestamp_list):
                cursor.execute("""
                    INSERT INTO timeseries_kinematics VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    activity_id, ts,
                    speed_list[i] if i < len(speed_list) else None,
                    distance_list[i] if i < len(distance_list) else None,
                    cadence_list[i] if i < len(cadence_list) else None,
                    stride_length_list[i] if i < len(stride_length_list) else None
                ))
            
            # Cardio
            heart_rate_list = activity_data.get('heart_rate_list') or []
            rr_interval_list = activity_data.get('rr_interval_list') or []
            
            for i, ts in enumerate(timestamp_list):
                cursor.execute("""
                    INSERT INTO timeseries_cardio VALUES (?, ?, ?, ?)
                """, (
                    activity_id, ts,
                    heart_rate_list[i] if i < len(heart_rate_list) else None,
                    rr_interval_list[i] if i < len(rr_interval_list) else None
                ))
            
            # Biomechanics
            ground_time_list = activity_data.get('ground_time_list') or []
            ground_time_balance_list = activity_data.get('ground_time_balance_list') or []
            oscillation_list = activity_data.get('oscillation_list') or []
            vertical_oscillation_balance_list = activity_data.get('vertical_oscillation_balance_list') or []
            leg_spring_list = activity_data.get('leg_spring_list') or []
            leg_spring_stiffness_balance_list = activity_data.get('leg_spring_stiffness_balance_list') or []
            impact_list = activity_data.get('impact_list') or []
            impact_loading_rate_balance_list = activity_data.get('impact_loading_rate_balance_list') or []
            vertical_ratio_list = activity_data.get('vertical_ratio_list') or []
            
            for i, ts in enumerate(timestamp_list):
                cursor.execute("""
                    INSERT INTO timeseries_biomechanics VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    activity_id, ts,
                    ground_time_list[i] if i < len(ground_time_list) else None,
                    ground_time_balance_list[i] if i < len(ground_time_balance_list) else None,
                    oscillation_list[i] if i < len(oscillation_list) else None,
                    vertical_oscillation_balance_list[i] if i < len(vertical_oscillation_balance_list) else None,
                    leg_spring_list[i] if i < len(leg_spring_list) else None,
                    leg_spring_stiffness_balance_list[i] if i < len(leg_spring_stiffness_balance_list) else None,
                    impact_list[i] if i < len(impact_list) else None,
                    impact_loading_rate_balance_list[i] if i < len(impact_loading_rate_balance_list) else None,
                    vertical_ratio_list[i] if i < len(vertical_ratio_list) else None
                ))
            
            # Elevation
            elevation_list = activity_data.get('elevation_list') or []
            grade_list = activity_data.get('grade_list') or []
            
            for i, ts in enumerate(timestamp_list):
                cursor.execute("""
                    INSERT INTO timeseries_elevation VALUES (?, ?, ?, ?)
                """, (
                    activity_id, ts,
                    elevation_list[i] if i < len(elevation_list) else None,
                    grade_list[i] if i < len(grade_list) else None
                ))
            
            # GPS points
            loc_list = activity_data.get('loc_list') or []
            for i, ts in enumerate(timestamp_list):
                if i < len(loc_list) and loc_list[i]:
                    cursor.execute("""
                        INSERT INTO gps_points VALUES (?, ?, ?, ?)
                    """, (
                        activity_id, ts,
                        loc_list[i].get('Lat'),
                        loc_list[i].get('Lng')
                    ))
        
        # Save laps
        events = activity_data.get('events', {})
        laps = events.get('laps', []) if events else []
        for lap_num, lap in enumerate(laps, 1):
            cursor.execute("""
                INSERT INTO laps VALUES (?, ?, ?, ?, ?)
            """, (
                activity_id,
                lap_num,
                lap.get('timestamp'),
                lap.get('trigger'),
                lap.get('workout_step')
            ))
        
        self.conn.commit()
        return True, "Activity saved successfully"
    
    def get_activity_count(self) -> int:
        """Get total number of activities in database"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM activities")
        return cursor.fetchone()[0]
