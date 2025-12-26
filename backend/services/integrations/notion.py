"""
Notion Integration Service
Handles Notion API for task mirroring
"""

from notion_client import Client
from typing import List, Dict, Optional
from datetime import datetime, date
from config.settings import get_settings
from loguru import logger

settings = get_settings()


class NotionService:
    """Notion API integration"""
    
    def __init__(self, access_token: str):
        """
        Initialize Notion client
        
        Args:
            access_token: Notion integration token
        """
        self.client = Client(auth=access_token)
    
    def search_databases(self, query: str = "") -> List[Dict]:
        """
        Search for databases in workspace
        
        Args:
            query: Optional search query
        
        Returns:
            List of database objects
        """
        try:
            response = self.client.search(
                query=query,
                filter={"property": "object", "value": "database"}
            )
            
            databases = []
            for db in response.get('results', []):
                databases.append({
                    'id': db['id'],
                    'title': db['title'][0]['plain_text'] if db['title'] else 'Untitled',
                    'url': db['url']
                })
            
            return databases
        
        except Exception as e:
            logger.error(f"Notion API error: {e}")
            raise
    
    def create_database(
        self,
        parent_page_id: str,
        title: str = "Study Tasks"
    ) -> str:
        """
        Create a new database in Notion
        
        Args:
            parent_page_id: Parent page ID
            title: Database title
        
        Returns:
            Database ID
        """
        try:
            database = self.client.databases.create(
                parent={"type": "page_id", "page_id": parent_page_id},
                title=[{"type": "text", "text": {"content": title}}],
                properties={
                    "Title": {"title": {}},
                    "Course": {"select": {}},
                    "Topics": {"multi_select": {}},
                    "Difficulty": {
                        "select": {
                            "options": [
                                {"name": "Easy", "color": "green"},
                                {"name": "Medium", "color": "yellow"},
                                {"name": "Hard", "color": "orange"},
                                {"name": "Exam Level", "color": "red"}
                            ]
                        }
                    },
                    "Due Date": {"date": {}},
                    "Status": {
                        "select": {
                            "options": [
                                {"name": "Not Started", "color": "gray"},
                                {"name": "In Progress", "color": "blue"},
                                {"name": "Completed", "color": "green"},
                                {"name": "Skipped", "color": "red"}
                            ]
                        }
                    },
                    "Duration (min)": {"number": {}},
                    "Mastery Impact": {"number": {}},
                    "Calendar Link": {"url": {}},
                    "Created": {"created_time": {}}
                }
            )
            
            logger.info(f"Created Notion database: {database['id']}")
            return database['id']
        
        except Exception as e:
            logger.error(f"Failed to create Notion database: {e}")
            raise
    
    def create_page(
        self,
        database_id: str,
        title: str,
        course: str,
        topics: List[str],
        difficulty: str,
        due_date: Optional[date] = None,
        status: str = "Not Started",
        duration_min: Optional[int] = None,
        mastery_impact: Optional[float] = None,
        calendar_link: Optional[str] = None
    ) -> str:
        """
        Create a page (task) in database
        
        Args:
            database_id: Database ID
            title: Task title
            course: Course name
            topics: List of topic names
            difficulty: Difficulty level
            due_date: Due date
            status: Task status
            duration_min: Duration in minutes
            mastery_impact: Expected mastery gain
            calendar_link: Link to Google Calendar event
        
        Returns:
            Page ID
        """
        try:
            properties = {
                "Title": {"title": [{"text": {"content": title}}]},
                "Course": {"select": {"name": course}},
                "Topics": {"multi_select": [{"name": topic} for topic in topics]},
                "Difficulty": {"select": {"name": difficulty}},
                "Status": {"select": {"name": status}}
            }
            
            if due_date:
                properties["Due Date"] = {"date": {"start": due_date.isoformat()}}
            
            if duration_min is not None:
                properties["Duration (min)"] = {"number": duration_min}
            
            if mastery_impact is not None:
                properties["Mastery Impact"] = {"number": mastery_impact}
            
            if calendar_link:
                properties["Calendar Link"] = {"url": calendar_link}
            
            page = self.client.pages.create(
                parent={"database_id": database_id},
                properties=properties
            )
            
            logger.info(f"Created Notion page: {page['id']}")
            return page['id']
        
        except Exception as e:
            logger.error(f"Failed to create Notion page: {e}")
            raise
    
    def update_page(
        self,
        page_id: str,
        title: Optional[str] = None,
        status: Optional[str] = None,
        due_date: Optional[date] = None,
        duration_min: Optional[int] = None,
        mastery_impact: Optional[float] = None
    ):
        """
        Update an existing page
        
        Args:
            page_id: Page ID to update
            title, status, due_date, etc: Fields to update
        """
        try:
            properties = {}
            
            if title:
                properties["Title"] = {"title": [{"text": {"content": title}}]}
            
            if status:
                properties["Status"] = {"select": {"name": status}}
            
            if due_date:
                properties["Due Date"] = {"date": {"start": due_date.isoformat()}}
            
            if duration_min is not None:
                properties["Duration (min)"] = {"number": duration_min}
            
            if mastery_impact is not None:
                properties["Mastery Impact"] = {"number": mastery_impact}
            
            if properties:
                page = self.client.pages.update(
                    page_id=page_id,
                    properties=properties
                )
                logger.info(f"Updated Notion page: {page_id}")
                return page
        
        except Exception as e:
            logger.error(f"Failed to update Notion page: {e}")
            raise
    
    def get_page(self, page_id: str) -> Dict:
        """
        Retrieve a page
        
        Args:
            page_id: Page ID
        
        Returns:
            Page object
        """
        try:
            return self.client.pages.retrieve(page_id=page_id)
        except Exception as e:
            logger.error(f"Failed to get Notion page: {e}")
            raise
    
    def query_database(
        self,
        database_id: str,
        filter_conditions: Optional[Dict] = None,
        sorts: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """
        Query database with filters
        
        Args:
            database_id: Database ID
            filter_conditions: Notion filter object
            sorts: List of sort objects
        
        Returns:
            List of page objects
        """
        try:
            query_params = {"database_id": database_id}
            
            if filter_conditions:
                query_params["filter"] = filter_conditions
            
            if sorts:
                query_params["sorts"] = sorts
            
            response = self.client.databases.query(**query_params)
            return response.get('results', [])
        
        except Exception as e:
            logger.error(f"Failed to query Notion database: {e}")
            raise
    
    def sync_task_to_notion(
        self,
        database_id: str,
        task_data: Dict,
        existing_page_id: Optional[str] = None
    ) -> str:
        """
        Sync a study task to Notion (create or update)
        
        Args:
            database_id: Notion database ID
            task_data: Task data dict
            existing_page_id: If provided, update existing page
        
        Returns:
            Page ID
        """
        if existing_page_id:
            # Update existing page
            self.update_page(
                page_id=existing_page_id,
                title=task_data.get('title'),
                status=task_data.get('status'),
                due_date=task_data.get('due_date'),
                duration_min=task_data.get('duration_min'),
                mastery_impact=task_data.get('mastery_impact')
            )
            return existing_page_id
        else:
            # Create new page
            return self.create_page(
                database_id=database_id,
                title=task_data['title'],
                course=task_data['course'],
                topics=task_data.get('topics', []),
                difficulty=task_data['difficulty'],
                due_date=task_data.get('due_date'),
                status=task_data.get('status', 'Not Started'),
                duration_min=task_data.get('duration_min'),
                mastery_impact=task_data.get('mastery_impact'),
                calendar_link=task_data.get('calendar_link')
            )
