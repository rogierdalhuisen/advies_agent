
import os
from typing import Dict
from vergelijker.premium_lookup import PremiumLookup
from vergelijker.data_loader import load_all_company_data, load_region_mapping
import math

class PremiumCalculator:
    """
    Calculator that takes premium lookup results and calculates total costs
    for all company-dekking-eigen_risico combinations for two datasets
    """

    def __init__(self, user_data: dict):
        """
        Initialize the calculator with premium lookup results from two datasets

        Args:
            user_data: User input data for premium lookup
        """
        # Store user data for use in company-specific calculations
        self.user_data = user_data

        base_data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        
        # Initialize both premium lookups
        self.international_health_lookup = PremiumLookup(os.path.join(base_data_path, 'internationale_ziektekostenverzekeringen_v11.xlsx'))
        self.travel_insurance_lookup = PremiumLookup(os.path.join(base_data_path, 'reisverzekeringen_v10.xlsx'))
        
        # Get premium data from both datasets
        self.international_health_data = self.international_health_lookup.get_premiums(user_data)
        self.travel_insurance_data = self.travel_insurance_lookup.get_premiums(user_data)

    def calculate_all_totals(self) -> Dict[str, Dict[str, Dict[str, Dict[str, float]]]]:
        """
        Calculate total costs for all company-dekking-eigen_risico combinations
        for both datasets

        Returns:
            {
                'Internationale Ziektekostenverzekeringen': {
                    'company_name': {
                        'Budget': {'0': 123.45, '250': 234.56, '500': 345.67, ...},
                        'Medium': {'0': 234.56, '250': 345.67, '500': 456.78, ...},
                        'Top': {'0': 345.67, '250': 456.78, '500': 567.89, ...}
                    },
                    ...
                },
                'Internationale Reisverzekeringen': {
                    'company_name': {
                        'Budget': {'0': 123.45, '250': 234.56, '500': 345.67, ...},
                        'Medium': {'0': 234.56, '250': 345.67, '500': 456.78, ...},
                        'Top': {'0': 345.67, '250': 456.78, '500': 567.89, ...}
                    },
                    ...
                }
            }
        """
        results = {}

        # Calculate totals for international health insurance
        international_health_totals = {}
        for company_name, company_data in self.international_health_data.items():
            company_totals = self._calculate_company_totals(company_name, company_data)
            international_health_totals[company_name] = company_totals

        # Calculate totals for travel insurance
        travel_insurance_totals = {}
        for company_name, company_data in self.travel_insurance_data.items():
            company_totals = self._calculate_company_totals(company_name, company_data)
            travel_insurance_totals[company_name] = company_totals

        # Return both datasets
        results['Internationale Ziektekostenverzekeringen'] = international_health_totals
        results['Internationale Reisverzekeringen'] = travel_insurance_totals

        return results

    def _calculate_company_totals(self, company_name: str, company_data: dict) -> Dict[str, Dict[str, float]]:
        """
        Calculate totals for a specific company using company-specific methods

        Args:
            company_name: Name of the insurance company
            company_data: Premium data for this company

        Returns:
            {
                'Budget': {'0': total, '100': total, '300': total, ...},
                'Medium': {'0': total, '100': total, '300': total, ...},
                'Top': {'0': total, '100': total, '300': total, ...}
            }
        """
        # Route to company-specific methods for future custom rules
        if company_name == 'Goudse Expat Pakket':
            return self._calculate_GEP_totals(company_data)
        else:
            # Default calculation for unknown companies
            return self._calculate_default_totals(company_data)

    def _calculate_GEP_totals(self, company_data: dict) -> Dict[str, Dict[str, float]]:
        """
        Calculate totals for GEP (company-specific rules can be added here)

        Args:
            company_data: Premium data for this company

        Returns:
            {'Budget': {'0': total, '100': total, ...}, 'Medium': {...}, 'Top': {...}}
        """
        totals = {}

        # Get family composition from user data (boolean values)
        has_partner = self.user_data.get('has_partner', False)
        has_children = self.user_data.get('children', False)

        # Get region from user data
        region = self.user_data.get('region', '')
        is_europa = region == 'Regio A'

        # Determine GEP yearly premium addition based on region and family composition
        if is_europa:
            if not has_partner and not has_children:
                gep_yearly_addition = 156.99
            elif has_partner and has_children:
                gep_yearly_addition = 396.98
            else:  # either partner or children
                gep_yearly_addition = 283.98
        else:  # not Europa (Excl.)
            if not has_partner and not has_children:
                gep_yearly_addition = 261.99
            elif has_partner and has_children:
                gep_yearly_addition = 606.98
            else:  # either partner or children
                gep_yearly_addition = 468.98

        # For each coverage level (Budget, Medium, Top)
        for dekking in ['Budget', 'Medium', 'Top']:
            dekking_totals = {}

            for eigen_risico in ['0', '250', '500', '1000', '2500']:
                total_cost = 0.0
                has_website = False
                has_valid_data = False
                has_nvt_or_invalid = False

                # Sum up costs for all people (main_person, partner, child_1, etc.)
                for person_type, person_data in company_data.items():
                    if dekking in person_data and eigen_risico in person_data[dekking]:
                        premium_value = person_data[dekking][eigen_risico]
                        if isinstance(premium_value, str) and premium_value.lower() == "website":
                            has_website = True
                            has_valid_data = True
                        elif isinstance(premium_value, str) and premium_value.lower() == "nvt":
                            has_nvt_or_invalid = True
                            has_valid_data = True
                        elif isinstance(premium_value, (int, float)):
                            total_cost += premium_value
                            has_valid_data = True
                        else:
                            # Any other invalid value (NaN, etc.)
                            has_nvt_or_invalid = True
                            has_valid_data = True

                # Add result based on what we found
                if has_valid_data:
                    if has_website:
                        dekking_totals[eigen_risico] = "website"
                    elif has_nvt_or_invalid:
                        # If ANY person has "nvt" or invalid data, mark entire combination as not available
                        dekking_totals[eigen_risico] = None
                    elif total_cost > 0:
                        # Add GEP-specific yearly premium addition
                        total_yearly_cost = total_cost + gep_yearly_addition
                        # Convert yearly premium to monthly by dividing by 12
                        dekking_totals[eigen_risico] = round(total_yearly_cost / 12, 2)
                    else:
                        # All premiums are 0 - mark as not available
                        dekking_totals[eigen_risico] = None

            # Only add dekking if it has at least one valid combination
            if dekking_totals:
                totals[dekking] = dekking_totals

        # Round all numeric values up to the next integer before returning
        for dekking in totals:
            for eigen_risico in totals[dekking]:
                if isinstance(totals[dekking][eigen_risico], (int, float)):
                    totals[dekking][eigen_risico] = math.ceil(totals[dekking][eigen_risico])
        return totals


    def _calculate_default_totals(self, company_data: dict) -> Dict[str, Dict[str, float]]:
        """
        Default calculation method - sums up premiums for all people for each combination

        Args:
            company_data: Premium data for the company

        Returns:
            {'Budget': {'0': total, '100': total, ...}, 'Medium': {...}, 'Top': {...}}
        """
        totals = {}

        # For each coverage level (Budget, Medium, Top)
        for dekking in ['Budget', 'Medium', 'Top']:
            dekking_totals = {}

            # For each eigen_risico option (0, 100, 300, 1000, 2500)
            for eigen_risico in ['0', '250', '500', '1000', '2500']:
                total_cost = 0.0
                has_website = False
                has_valid_data = False
                has_nvt_or_invalid = False

                # Sum up costs for all people (main_person, partner, child_1, etc.)
                for person_type, person_data in company_data.items():
                    if dekking in person_data and eigen_risico in person_data[dekking]:
                        premium_value = person_data[dekking][eigen_risico]
                        if isinstance(premium_value, str) and premium_value.lower() == "website":
                            has_website = True
                            has_valid_data = True
                        elif isinstance(premium_value, str) and premium_value.lower() == "nvt":
                            has_nvt_or_invalid = True
                            has_valid_data = True
                        elif isinstance(premium_value, (int, float)):
                            total_cost += premium_value
                            has_valid_data = True
                        else:
                            # Any other invalid value (NaN, etc.)
                            has_nvt_or_invalid = True
                            has_valid_data = True

                # Add result based on what we found
                if has_valid_data:
                    if has_website:
                        dekking_totals[eigen_risico] = "website"
                    elif has_nvt_or_invalid:
                        # If ANY person has "nvt" or invalid data, mark entire combination as not available
                        dekking_totals[eigen_risico] = None
                    elif total_cost > 0:
                        # Convert yearly premium to monthly by dividing by 12
                        dekking_totals[eigen_risico] = round(total_cost / 12, 2)
                    else:
                        # All premiums are 0 - mark as not available
                        dekking_totals[eigen_risico] = None

            # Only add dekking if it has at least one valid combination
            if dekking_totals:
                totals[dekking] = dekking_totals

        # Round all numeric values up to the next integer before returning
        for dekking in totals:
            for eigen_risico in totals[dekking]:
                if isinstance(totals[dekking][eigen_risico], (int, float)):
                    totals[dekking][eigen_risico] = math.ceil(totals[dekking][eigen_risico])

        return totals