from app import db
from app.models import Geofence, User
from geopy.distance import geodesic

class GeofenceService:
    """Service for managing geofences"""
    
    @staticmethod
    def create_geofence(user_id, name, center_latitude, center_longitude, 
                       radius_meters, label=None):
        """
        Create a new geofence
        
        Args:
            user_id: User ID
            name: Geofence name
            center_latitude: Center latitude
            center_longitude: Center longitude
            radius_meters: Radius in meters
            label: Optional label (e.g., 'home', 'school')
            
        Returns:
            Geofence object
        """
        # Validate user exists
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        geofence = Geofence(
            user_id=user_id,
            name=name,
            center_latitude=center_latitude,
            center_longitude=center_longitude,
            radius_meters=radius_meters,
            label=label
        )
        
        db.session.add(geofence)
        db.session.commit()
        
        return geofence
    
    @staticmethod
    def update_geofence(geofence_id, name=None, center_latitude=None, 
                       center_longitude=None, radius_meters=None, label=None, 
                       active=None):
        """
        Update existing geofence
        
        Args:
            geofence_id: Geofence ID
            **kwargs: Fields to update
            
        Returns:
            Updated Geofence object
        """
        geofence = Geofence.query.get(geofence_id)
        if not geofence:
            raise ValueError(f"Geofence {geofence_id} not found")
        
        if name is not None:
            geofence.name = name
        if center_latitude is not None:
            geofence.center_latitude = center_latitude
        if center_longitude is not None:
            geofence.center_longitude = center_longitude
        if radius_meters is not None:
            geofence.radius_meters = radius_meters
        if label is not None:
            geofence.label = label
        if active is not None:
            geofence.active = active
        
        db.session.commit()
        
        return geofence
    
    @staticmethod
    def delete_geofence(geofence_id):
        """
        Delete geofence
        
        Args:
            geofence_id: Geofence ID
            
        Returns:
            True if deleted
        """
        geofence = Geofence.query.get(geofence_id)
        if geofence:
            db.session.delete(geofence)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def get_user_geofences(user_id):
        """Get all geofences for a user"""
        return Geofence.query.filter_by(user_id=user_id).all()
    
    @staticmethod
    def check_point_in_geofences(user_id, latitude, longitude):
        """
        Check if a point is inside any of the user's geofences
        
        Returns:
            tuple: (is_inside, geofence)
        """
        geofences = Geofence.query.filter_by(user_id=user_id, active=True).all()
        
        for geofence in geofences:
            if geofence.contains_point(latitude, longitude):
                return (True, geofence)
        
        return (False, None)
    
    @staticmethod
    def calculate_distance(point1, point2):
        """
        Calculate distance between two points in meters
        
        Args:
            point1: (lat, lon) tuple
            point2: (lat, lon) tuple
            
        Returns:
            Distance in meters
        """
        return geodesic(point1, point2).meters



