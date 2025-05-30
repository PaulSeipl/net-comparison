from typing import Dict


class ConnectionTypeMapper:
    """
    Maps connection types between different formats.
    """
    
    # Map from API response format to schema enum format
    SCHEMA_MAPPING: Dict[str, str] = {
        'DSL': 'DSL',
        'CABLE': 'Cable', 
        'FIBER': 'Fiber',
        'MOBILE': 'Mobile'
    }
    
    @classmethod
    def map_connection_type(cls, api_connection_type: str) -> str:
        """
        Map WebWunder API connection type to schema format.
        
        Args:
            api_connection_type: Connection type from WebWunder API
            
        Returns:
            Connection type in schema format
        """
        return cls.SCHEMA_MAPPING.get(
            api_connection_type, 
            api_connection_type
        )
