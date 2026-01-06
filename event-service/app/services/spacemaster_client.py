import requests
from typing import Optional, Dict, Any
from datetime import datetime
from app.constants import SPACEMASTER_GRAPHQL


class SpaceMasterClient:
    """Client untuk consume GraphQL API dari SpaceMaster service"""
    
    def __init__(self, endpoint: str = SPACEMASTER_GRAPHQL):
        self.endpoint = endpoint
        self.headers = {
            "Content-Type": "application/json",
            "ngrok-skip-browser-warning": "true"
        }
    
    def _execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute GraphQL query ke SpaceMaster API
        """
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            result = {}
            try:
                result = response.json()
            except:
                pass

            if "errors" in result:
                error_messages = [err.get("message", "Unknown error") for err in result["errors"]]
                raise Exception(f"SpaceMaster API error: {', '.join(error_messages)}")

            response.raise_for_status()
            return result.get("data", {})
            
        except requests.exceptions.Timeout:
            raise Exception("SpaceMaster API timeout. Please try again later.")
        except requests.exceptions.ConnectionError:
            raise Exception("Cannot connect to SpaceMaster API. Please check the service availability.")
        except Exception as e:
            if isinstance(e, requests.exceptions.HTTPError) and result.get("errors"):
                raise
            raise Exception(f"SpaceMaster API request failed: {str(e)}")
    
    def get_venue(self, venue_id: int) -> Optional[Dict[str, Any]]:
        """Get venue by ID"""
        query = """
        query {
          venues {
            id
            name
            city
          }
        }
        """
        data = self._execute_query(query)
        venues = data.get("venues", [])
        for venue in venues:
            if int(venue.get("id")) == venue_id:
                return venue
        return None
    
    def get_rooms_by_venue(self, venue_id: int) -> list:
        """Get semua rooms di venue tertentu"""
        query = """
        query($venueId: ID!) {
          roomsByVenue(venueId: $venueId) {
            id
            name
            capacity
          }
        }
        """
        variables = {"venueId": str(venue_id)}
        data = self._execute_query(query, variables)
        return data.get("roomsByVenue", [])
    
    def get_room(self, venue_id: int, room_id: int) -> Optional[Dict[str, Any]]:
        """Get room by venue_id dan room_id"""
        rooms = self.get_rooms_by_venue(venue_id)
        for room in rooms:
            if int(room.get("id")) == room_id:
                return room
        return None
    
    def check_room_availability(
        self, 
        room_id: int, 
        start_time: datetime, 
        end_time: datetime,
        exclude_event_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Check apakah room tersedia pada waktu tertentu"""
        query = """
        query {
          schedules {
            id
            roomId
            startTime
            endTime
            status
          }
        }
        """
        data = self._execute_query(query)
        schedules = data.get("schedules", [])
        room_schedules = [s for s in schedules if int(s.get("roomId")) == room_id]
        
        for schedule in room_schedules:
            if exclude_event_id and str(schedule.get("id")) == str(exclude_event_id):
                continue
            if schedule.get("status") in ["CANCELLED", "AVAILABLE"]:
                continue
            
            try:
                # Normalisasi format time (beberapa API pake spasi, beberapa pake T)
                # Kita coba bersihkan agar isoformat aman
                s_start = schedule.get("startTime", "").replace(" ", "T")
                s_end = schedule.get("endTime", "").replace(" ", "T")
                
                # Jika pecah (misal cuma tanggal), tambahkan jam default
                if len(s_start) == 10: s_start += "T00:00:00"
                if len(s_end) == 10: s_end += "T00:00:00"

                schedule_start = datetime.fromisoformat(s_start)
                schedule_end = datetime.fromisoformat(s_end)
                
                if start_time < schedule_end and end_time > schedule_start:
                    return {"is_available": False, "conflict": schedule}
            except (ValueError, TypeError):
                continue
        
        return {"is_available": True}
    
    def block_schedule(self, room_id: int, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """
        Push schedule baru ke SpaceMaster API menggunakan mutation blockSchedule
        dengan argumen INPUT (BlockScheduleInput) sesuai error log terbaru.
        """
        mutation = """
        mutation($input: BlockScheduleInput!) {
          blockSchedule(input: $input) {
            success
            message
          }
        }
        """
        
        variables = {
            "input": {
                "roomId": int(room_id),
                "startTime": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "endTime": end_time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
        return self._execute_query(mutation, variables)
    
    def validate_venue_and_room(
        self, 
        venue_id: int, 
        room_id: int, 
        start_time: datetime, 
        end_time: datetime,
        exclude_event_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validasi venue, room, dan availability sekaligus"""
        venue = self.get_venue(venue_id)
        if not venue:
            raise Exception(f"Venue with ID '{venue_id}' not found in SpaceMaster")
        
        room = self.get_room(venue_id, room_id)
        if not room:
            raise Exception(f"Room with ID '{room_id}' not found in venue '{venue_id}'")
        
        availability = self.check_room_availability(room_id, start_time, end_time, exclude_event_id)
        if not availability["is_available"]:
            conflict = availability["conflict"]
            raise Exception(
                f"Room ini already booked from {conflict.get('startTime')} to {conflict.get('endTime')} (SpaceMaster)"
            )
        
        return {
            "venue": venue,
            "room": room,
            "capacity": room.get("capacity", 0)
        }


# Singleton instance
_client = None

def get_spacemaster_client() -> SpaceMasterClient:
    """Get singleton instance of SpaceMasterClient"""
    global _client
    if _client is None:
        _client = SpaceMasterClient()
    return _client
