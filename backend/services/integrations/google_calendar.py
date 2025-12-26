"""
Google Calendar Integration Service
Handles OAuth, event creation, and calendar sync
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from config.settings import get_settings
from loguru import logger

settings = get_settings()


class GoogleCalendarService:
    """Google Calendar API integration"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events'
    ]
    
    def __init__(self):
        self.client_id = settings.google_client_id
        self.client_secret = settings.google_client_secret
        self.redirect_uri = settings.google_redirect_uri
    
    def get_auth_url(self, state: str) -> str:
        """
        Generate OAuth authorization URL
        
        Args:
            state: State parameter for security
        
        Returns:
            Authorization URL for user to visit
        """
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uris": [self.redirect_uri],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=self.SCOPES,
            redirect_uri=self.redirect_uri
        )
        
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            state=state,
            prompt='consent'
        )
        
        return auth_url
    
    def exchange_code_for_tokens(self, code: str) -> Dict[str, str]:
        """
        Exchange authorization code for access and refresh tokens
        
        Args:
            code: Authorization code from OAuth callback
        
        Returns:
            Dict with access_token, refresh_token, and expiry
        """
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uris": [self.redirect_uri],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=self.SCOPES,
            redirect_uri=self.redirect_uri
        )
        
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        return {
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_expiry': credentials.expiry.isoformat() if credentials.expiry else None
        }
    
    def get_service(self, access_token: str, refresh_token: str):
        """
        Get authenticated Google Calendar service
        
        Args:
            access_token: Access token
            refresh_token: Refresh token
        
        Returns:
            Google Calendar service object
        """
        credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        
        return build('calendar', 'v3', credentials=credentials)
    
    def list_calendars(self, access_token: str, refresh_token: str) -> List[Dict]:
        """
        List all calendars for user
        
        Returns:
            List of calendar dicts with id, name, and primary status
        """
        try:
            service = self.get_service(access_token, refresh_token)
            calendar_list = service.calendarList().list().execute()
            
            calendars = []
            for cal in calendar_list.get('items', []):
                calendars.append({
                    'id': cal['id'],
                    'name': cal['summary'],
                    'primary': cal.get('primary', False),
                    'color': cal.get('backgroundColor', '#3B82F6')
                })
            
            return calendars
        
        except HttpError as e:
            logger.error(f"Google Calendar API error: {e}")
            raise
    
    def create_calendar(
        self,
        access_token: str,
        refresh_token: str,
        name: str = "Study Planner"
    ) -> str:
        """
        Create a new calendar
        
        Args:
            name: Calendar name
        
        Returns:
            Calendar ID
        """
        try:
            service = self.get_service(access_token, refresh_token)
            
            calendar = {
                'summary': name,
                'description': 'Adaptive Study Planner - Automatically generated study schedule',
                'timeZone': 'UTC'
            }
            
            created = service.calendars().insert(body=calendar).execute()
            
            logger.info(f"Created calendar: {created['id']}")
            return created['id']
        
        except HttpError as e:
            logger.error(f"Failed to create calendar: {e}")
            raise
    
    def create_event(
        self,
        access_token: str,
        refresh_token: str,
        calendar_id: str,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: str = "",
        location: str = ""
    ) -> str:
        """
        Create a calendar event
        
        Args:
            calendar_id: Calendar ID to add event to
            title: Event title
            start_time: Event start (datetime with timezone)
            end_time: Event end (datetime with timezone)
            description: Event description
            location: Event location
        
        Returns:
            Event ID
        """
        try:
            service = self.get_service(access_token, refresh_token)
            
            event = {
                'summary': title,
                'description': description,
                'location': location,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC'
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC'
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 10}
                    ]
                }
            }
            
            created = service.events().insert(
                calendarId=calendar_id,
                body=event
            ).execute()
            
            logger.info(f"Created event: {created['id']}")
            return created['id']
        
        except HttpError as e:
            logger.error(f"Failed to create event: {e}")
            raise
    
    def update_event(
        self,
        access_token: str,
        refresh_token: str,
        calendar_id: str,
        event_id: str,
        title: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        description: Optional[str] = None
    ):
        """
        Update an existing event
        
        Args:
            calendar_id: Calendar ID
            event_id: Event ID to update
            title, start_time, end_time, description: Fields to update
        """
        try:
            service = self.get_service(access_token, refresh_token)
            
            # Get existing event
            event = service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            # Update fields
            if title:
                event['summary'] = title
            if description:
                event['description'] = description
            if start_time:
                event['start'] = {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC'
                }
            if end_time:
                event['end'] = {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC'
                }
            
            updated = service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            logger.info(f"Updated event: {event_id}")
            return updated
        
        except HttpError as e:
            logger.error(f"Failed to update event: {e}")
            raise
    
    def delete_event(
        self,
        access_token: str,
        refresh_token: str,
        calendar_id: str,
        event_id: str
    ):
        """Delete a calendar event"""
        try:
            service = self.get_service(access_token, refresh_token)
            service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            logger.info(f"Deleted event: {event_id}")
        
        except HttpError as e:
            logger.error(f"Failed to delete event: {e}")
            raise
    
    def get_events(
        self,
        access_token: str,
        refresh_token: str,
        calendar_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """
        Get all events in date range
        
        Args:
            calendar_id: Calendar ID (or 'primary')
            start_date: Start of range
            end_date: End of range
        
        Returns:
            List of event dicts
        """
        try:
            service = self.get_service(access_token, refresh_token)
            
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=start_date.isoformat() + 'Z',
                timeMax=end_date.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = []
            for event in events_result.get('items', []):
                events.append({
                    'id': event['id'],
                    'title': event.get('summary', 'Untitled'),
                    'start': event['start'].get('dateTime', event['start'].get('date')),
                    'end': event['end'].get('dateTime', event['end'].get('date')),
                    'description': event.get('description', ''),
                    'location': event.get('location', '')
                })
            
            return events
        
        except HttpError as e:
            logger.error(f"Failed to get events: {e}")
            raise
    
    def get_busy_times(
        self,
        access_token: str,
        refresh_token: str,
        calendar_ids: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """
        Get all busy time blocks across multiple calendars
        
        Args:
            calendar_ids: List of calendar IDs to check
            start_date: Start of range
            end_date: End of range
        
        Returns:
            List of busy time blocks
        """
        try:
            service = self.get_service(access_token, refresh_token)
            
            body = {
                "timeMin": start_date.isoformat() + 'Z',
                "timeMax": end_date.isoformat() + 'Z',
                "items": [{"id": cal_id} for cal_id in calendar_ids]
            }
            
            response = service.freebusy().query(body=body).execute()
            
            busy_times = []
            for cal_id, cal_data in response.get('calendars', {}).items():
                for busy in cal_data.get('busy', []):
                    busy_times.append({
                        'calendar_id': cal_id,
                        'start': busy['start'],
                        'end': busy['end']
                    })
            
            return busy_times
        
        except HttpError as e:
            logger.error(f"Failed to get busy times: {e}")
            raise
