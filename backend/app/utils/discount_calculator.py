"""
Discount calculation utilities for WebWunder offers.
"""
from math import floor
from pydantic import BaseModel


class DiscountResult(BaseModel):
    monthly_discount: int | None = None
    monthly_cost_with_discount: int | None = None
    total_savings: int | None = None
    discount_percentage: int | None = None


class DiscountCalculator:
    """
    Calculates discounts for WebWunder offers based on voucher types.
    """
    
    def __init__(self, promotion_length: int = 24):
        self.promotion_length = promotion_length

    def calculate_discount(
        self, 
        base_monthly_cost: int,
        voucher_percentage: int | None = None,
        max_discount_in_cent: int | None = None,
        discount_in_cent: int | None = None
    ) -> DiscountResult:
        """
        Calculate discount based on voucher type.
        
        Args:
            base_monthly_cost: Base monthly cost in cents
            voucher_percentage: Percentage discount (if percentage voucher)
            max_discount_in_cent: Maximum discount cap in cents
            discount_in_cent: Absolute discount in cents (if absolute voucher)
            
        Returns:
            DiscountResult object with calculated values
        """
        if voucher_percentage:
            return self._calculate_percentage_discount(
                base_monthly_cost, voucher_percentage, max_discount_in_cent
            )
        elif discount_in_cent:
            return self._calculate_absolute_discount(base_monthly_cost, discount_in_cent)
        else:
            return DiscountResult()

    def _calculate_percentage_discount(
        self, 
        base_monthly_cost: int, 
        voucher_percentage: int, 
        max_discount: int | None = None
    ) -> DiscountResult:
        """
        Calculate discount for percentage-based vouchers.
        
        Args:
            base_monthly_cost: Base monthly cost in cents
            voucher_percentage: Percentage discount
            max_discount: Maximum discount cap in cents
            
        Returns:
            DiscountResult with calculated percentage discount
        """
        # Default to very high value if max discount not specified
        max_discount = max_discount or 10**10
        
        # Calculate monthly discount based on percentage
        monthly_discount_temp = int(base_monthly_cost * (voucher_percentage / 100))
        complete_discount = monthly_discount_temp * self.promotion_length
        
        # Cap the discount by max discount
        absolute_discount = min(complete_discount, max_discount)
        
        # Calculate final values
        monthly_discount = absolute_discount // self.promotion_length
        monthly_cost_with_discount = round(base_monthly_cost - monthly_discount)
        discount_percentage = floor((monthly_discount / base_monthly_cost) * 100)
        
        return DiscountResult(
            monthly_discount=monthly_discount,
            monthly_cost_with_discount=monthly_cost_with_discount,
            total_savings=absolute_discount,
            discount_percentage=discount_percentage
        )

    def _calculate_absolute_discount(
        self, 
        base_monthly_cost: int, 
        discount_in_cent: int
    ) -> DiscountResult:
        """
        Calculate discount for absolute vouchers (distributed over promotion period).
        
        Args:
            base_monthly_cost: Base monthly cost in cents
            discount_in_cent: Absolute discount in cents
            
        Returns:
            DiscountResult with calculated absolute discount
        """
        monthly_discount = int(discount_in_cent / self.promotion_length)
        monthly_cost_with_discount = base_monthly_cost - monthly_discount
        discount_percentage = floor((monthly_discount / base_monthly_cost) * 100)
        
        return DiscountResult(
            monthly_discount=monthly_discount,
            monthly_cost_with_discount=monthly_cost_with_discount,
            total_savings=discount_in_cent,
            discount_percentage=discount_percentage
        )
        
        
class BytMeDiscountCalculator:
    """
    Calculates discounts for ByteMe offers based on voucher types.
    """
    
    def __init__(self, promotion_length: int = 24):
        self.promotion_length = promotion_length
