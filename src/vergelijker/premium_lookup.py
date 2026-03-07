import os
import pandas as pd
from typing import Dict, List, Optional
from vergelijker.data_loader import load_region_mapping, load_all_company_data

class PremiumLookup:
    """
    Simple class to look up insurance premiums from Excel data
    """
    
    def __init__(self, data_path: str):
        """
        Initialize with data from specified Excel file path
        
        Args:
            data_path: Path to the Excel file containing premium data
        """
        # Store the data path
        self.data_path = data_path
        
        # Load region mapping (country -> region per company)
        self.region_mapping = load_region_mapping(data_path)
        
        # Load all company premium data
        self.company_data = load_all_company_data(data_path)
        
    def get_premiums(self, user_data: dict) -> Dict[str, Dict[str, Dict[str, Dict[str, float]]]]:
        """
        Get all premium options for all people in the group
        
        user_data keys:
        - age: int (0-100) - main person's age
        - destination: str (country name like "Netherlands", "Germany")
        - has_partner: bool (whether there is a partner)
        - age_partner: int (partner's age, only used if has_partner is True)
        - children: bool (whether there are children)
        - child_ages: List[int] (ages of all children, only used if children is True)
        
        Returns:
        {
            'company_name': {
                'main_person': {
                    'Budget': {'0': 45.50, '100': 42.30, ...},
                    'Medium': {'0': 65.20, '100': 61.80, ...},
                    'Top': {'0': 85.90, '100': 82.10, ...}
                },
                'partner': {
                    'Budget': {'0': 38.20, '100': 35.10, ...},
                    ...
                },
                'child_1': {
                    'Budget': {'0': 25.30, '100': 22.80, ...},
                    ...
                },
                'child_2': {
                    ...
                }
            },
            ...
        }
        """
        destination = user_data['destination']
        main_age = user_data['age']
        has_partner = user_data.get('has_partner', False)
        age_partner = user_data.get('age_partner', None)
        children = user_data.get('children', False)
        child_ages = user_data.get('child_ages', [])
        
        # Build list of all people with their ages
        people = [('main_person', main_age)]
        
        if has_partner and age_partner is not None:
            people.append(('partner', age_partner))
        
        if children and child_ages:
            for i, child_age in enumerate(child_ages, 1):
                people.append((f'child_{i}', child_age))
        
        results = {}
        
        # Go through each insurance company
        for company_name, premium_df in self.company_data.items():
            
            # Get the region for this country and company
            if company_name not in self.region_mapping:
                continue
                
            if destination not in self.region_mapping[company_name]:
                continue
                
            region = self.region_mapping[company_name][destination]
            
            # Check if region is empty or problematic
            if region == '' or region is None or (isinstance(region, float) and pd.isna(region)):
                continue
            
            # Convert region to string to match column names (in case it's an integer)
            region_str = str(region)
                
            company_results = {}
            
            # Get premiums for each person
            for person_type, age in people:
                
                # Check if this age exists in the data
                if age not in premium_df.index:
                    continue
                
                person_premiums = {}
                
                # Get all insurance levels (Budget, Medium, Top)
                for level in ['Budget', 'Medium', 'Top']:
                    level_premiums = {}
                    
                    # Get all own risk options (0, 100, 300, 1000, 2500)
                    for own_risk in [0, 250, 500, 1000, 2500]:
                        try:
                            # Check if this column combination exists
                            if (region_str, level, own_risk) not in premium_df.columns:
                                continue
                            
                            premium = premium_df.loc[age, (region_str, level, own_risk)]
                            
                            # Handle case where premium might be a Series instead of scalar
                            if isinstance(premium, pd.Series):
                                if premium.empty:
                                    continue
                                premium = premium.iloc[0]  # Take first value if Series
                            
                            # Only add if it's a valid number (not NaN), "website", or "nvt"
                            if pd.notna(premium) and premium is not None:
                                if isinstance(premium, str) and premium.lower() == "website":
                                    level_premiums[str(own_risk)] = "website"
                                elif isinstance(premium, str) and premium.lower() == "nvt":
                                    level_premiums[str(own_risk)] = "nvt"
                                else:
                                    level_premiums[str(own_risk)] = round(float(premium), 2)
                        except (KeyError, IndexError, ValueError, TypeError):
                            # This combination doesn't exist or has invalid data, skip it
                            continue
                    
                    # Only add the level if it has at least one valid premium
                    if level_premiums:
                        person_premiums[level] = level_premiums
                
                # Only add the person if they have at least one valid premium
                if person_premiums:
                    company_results[person_type] = person_premiums
            
            # Only add the company if it has at least one person with valid premiums
            if company_results:
                results[company_name] = company_results
        
        return results
