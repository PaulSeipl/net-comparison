import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from app.schemas import WebWunderProduct


class WebWunderXMLParser:
    """
    Handles XML parsing for WebWunder SOAP responses.
    """
    
    NAMESPACES = {
        "SOAP-ENV": "http://schemas.xmlsoap.org/soap/envelope/",
        "ns2": "http://webwunder.gendev7.check24.fun/offerservice",
    }

    @classmethod
    def parse_response(cls, xml_response: str) -> List[WebWunderProduct]:
        """
        Parse WebWunder XML response and extract product information.
        
        Args:
            xml_response: Raw XML response from WebWunder API
            
        Returns:
            List of WebWunderProduct objects
        """
        try:
            root = ET.fromstring(xml_response)
            products = root.findall(".//ns2:products", cls.NAMESPACES)
            
            product_list = []
            for product in products:
                product_data = cls._extract_product_data(product)
                if product_data:
                    product_list.append(WebWunderProduct(**product_data))
                    
            return product_list
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML response: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing XML response: {e}")

    @classmethod
    def _extract_product_data(cls, product_element: ET.Element) -> Optional[Dict[str, Any]]:
        """
        Extract product data from a single product XML element.
        
        Args:
            product_element: XML element containing product information
            
        Returns:
            Dictionary with product data or None if extraction fails
        """
        try:
            # Extract voucher information
            voucher_data = cls._extract_voucher_data(product_element)
            
            # Extract basic product information
            product_data = {
                "product_id": cls._get_text_safe(product_element, "ns2:productId"),
                "provider_name": cls._get_text_safe(product_element, "ns2:providerName"),
                "speed": cls._get_int_safe(product_element, ".//ns2:speed"),
                "monthly_cost_in_cent": cls._get_int_safe(product_element, ".//ns2:monthlyCostInCent"),
                "monthly_cost_in_cent_from_25th_month": cls._get_int_safe(
                    product_element, ".//ns2:monthlyCostInCentFrom25thMonth"
                ),
                "contract_duration_in_months": cls._get_int_safe(
                    product_element, ".//ns2:contractDurationInMonths"
                ),
                "connection_type": cls._get_text_safe(product_element, ".//ns2:connectionType"),
                **voucher_data
            }
            
            # Validate required fields
            required_fields = ["product_id", "provider_name", "speed", "monthly_cost_in_cent"]
            if any(product_data.get(field) is None for field in required_fields):
                return None
                
            return product_data
            
        except Exception:
            return None

    @classmethod
    def _extract_voucher_data(cls, product_element: ET.Element) -> Dict[str, Optional[int]]:
        """
        Extract voucher information from product element.
        
        Args:
            product_element: XML element containing product information
            
        Returns:
            Dictionary with voucher data
        """
        return {
            "voucher_percentage": cls._get_int_safe(product_element, ".//ns2:percentage"),
            "max_discount_in_cent": cls._get_int_safe(product_element, ".//ns2:maxDiscountInCent"),
            "discount_in_cent": cls._get_int_safe(product_element, ".//ns2:discountInCent"),
            "min_order_value_in_cent": cls._get_int_safe(product_element, ".//ns2:minOrderValueInCent"),
        }

    @classmethod
    def _get_text_safe(cls, element: ET.Element, xpath: str) -> Optional[str]:
        """
        Safely extract text from XML element.
        
        Args:
            element: XML element to search in
            xpath: XPath expression
            
        Returns:
            Text content or None if not found
        """
        found_element = element.find(xpath, cls.NAMESPACES)
        return found_element.text if found_element is not None else None

    @classmethod
    def _get_int_safe(cls, element: ET.Element, xpath: str) -> Optional[int]:
        """
        Safely extract integer from XML element.
        
        Args:
            element: XML element to search in
            xpath: XPath expression
            
        Returns:
            Integer value or None if not found or invalid
        """
        text = cls._get_text_safe(element, xpath)
        try:
            return int(text) if text is not None else None
        except (ValueError, TypeError):
            return None
