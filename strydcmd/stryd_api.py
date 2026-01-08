"""Client for interacting with the Stryd API"""

import datetime
import os
import requests
from typing import Dict, List, Optional


class StrydAPI:
    """Client for interacting with the Stryd API"""
    
    BASE_URL = "https://www.stryd.com/b"
    
    def __init__(self, email: str, password: str):
        """
        Initialize Stryd API client
        
        Args:
            email: Stryd account email
            password: Stryd account password
        """
        self.email = email
        self.password = password
        self.session_id: Optional[str] = None
        self.user_id: Optional[str] = None
    
    def authenticate(self) -> str:
        """
        Authenticate with Stryd API
        
        Returns:
            Session ID token
            
        Raises:
            Exception: If authentication fails
        """
        request_json = {
            "email": self.email,
            "password": self.password
        }
        
        url = f"{self.BASE_URL}/email/signin"
        
        try:
            response = requests.post(url, json=request_json)
            
            if response.status_code != 200:
                raise Exception(
                    f"Authentication failed: {response.status_code} - {response.text}"
                )
            
            data = response.json()
            self.session_id = data.get('token')
            self.user_id = data.get('id')
            
            if not self.session_id:
                raise Exception("Authentication response missing token")
            
            print("✓ Successfully authenticated with Stryd")
            return self.session_id
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error during authentication: {e}")
    
    def is_authenticated(self) -> bool:
        """
        Check if client is authenticated
        
        Returns:
            True if session_id is set, False otherwise
        """
        return self.session_id is not None
    
    def get_activities(self, days: int = 30) -> List[Dict]:
        """
        Get activities from the last N days
        
        Args:
            days: Number of days to look back (default: 30)
            
        Returns:
            List of activity dictionaries
        """
        if not self.session_id:
            self.authenticate()
        
        # Calculate date range
        end_date = datetime.datetime.now() + datetime.timedelta(days=1)
        start_date = end_date - datetime.timedelta(days=days)
        
        # Set up request
        headers = {
            'Authorization': f'Bearer: {self.session_id}'
        }
        
        # Format dates
        start_str = start_date.strftime("%m-%d-%Y")
        end_str = end_date.strftime("%m-%d-%Y")
        
        print(f"\nRequesting activities from {start_str} to {end_str}")
        
        # Use users/calendar endpoint
        url = f"{self.BASE_URL}/api/v1/users/calendar"
        params = {
            'srtDate': start_str,
            'endDate': end_str,
            'sortBy': 'StartDate'
        }
        
        # Make request
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            error_msg = f"Failed to fetch activities: {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f" - {error_detail}"
            except:
                error_msg += f" - {response.text}"
            raise Exception(error_msg)
        
        data = response.json()
        activities = data.get('activities', [])
        
        # Debug: show date range of returned activities
        if activities:
            timestamps = [a.get('timestamp', 0) for a in activities if a.get('timestamp')]
            if timestamps:
                min_ts = min(timestamps)
                max_ts = max(timestamps)
                min_date = datetime.datetime.fromtimestamp(min_ts).strftime("%Y-%m-%d")
                max_date = datetime.datetime.fromtimestamp(max_ts).strftime("%Y-%m-%d")
                print(f"API returned {len(activities)} activities from {min_date} to {max_date}")
        
        return activities
    
    def download_fit_file(self, activity_id: str, output_dir: str = "fit_files", filename: Optional[str] = None) -> Optional[str]:
        """
        Download FIT file for a specific activity
        
        Args:
            activity_id: The activity ID
            output_dir: Directory where to save the FIT file (default: "fit_files")
            filename: Optional custom filename (without extension). If None, uses activity_id
            
        Returns:
            Path to the downloaded file, or None if failed
        """
        if not self.session_id:
            self.authenticate()
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        headers = {
            'Authorization': f'Bearer: {self.session_id}'
        }
        
        # Try the FIT file endpoint
        url = f"{self.BASE_URL}/api/v1/activities/{activity_id}/fit"
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                # Save the file
                if filename:
                    file_basename = f"{filename}.fit"
                else:
                    file_basename = f"{activity_id}.fit"
                filepath = os.path.join(output_dir, file_basename)
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                return filepath
            else:
                return None
                
        except requests.exceptions.RequestException:
            return None
