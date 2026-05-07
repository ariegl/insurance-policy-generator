"""Schema registry for insurance policy types.

Each policy type is defined by a set of field names and the corresponding
Faker provider that should be used to generate a plausible fake value.
The registry is used by data_generator.py to create synthetic policies
without hard-coding any particular insurance type.
"""

from typing import Any, Dict, List, Optional, Type

# A schema definition maps a human‑readable field name (e.g. "policy_id")
# to a Faker method string or a two‑element list/tuple where:
#   first element = method name (e.g. "pyint")
#   second element = dict of keyword arguments for that method
# Simple fields that need no arguments are stored as plain strings.
SchemaFieldDef = str | List[Any] | tuple[Any, ...]
SchemaDefinition = Dict[str, SchemaFieldDef]


class BaseSchema:
    """Base schema that every concrete policy type must implement."""

    def get_fields(self) -> SchemaDefinition:
        """Return the definition of all fields for this policy type."""
        raise NotImplementedError


class MedicalInsurance(BaseSchema):
    """Fields specific to a medical insurance policy."""

    def get_fields(self) -> SchemaDefinition:
        return {
            "policy_id": "uuid4",
            "holder_name": "name",
            "holder_address": "address",
            "blood_type": ["random_element", {"elements": ["A+","A-","B+","B-","AB+","AB-","O+","O-"]}],
            "provider_network": "company",
            "deductible": ["pyint", {"min_value": 500, "max_value": 5000}],
            "premium_amount": ["pyint", {"min_value": 200, "max_value": 2000}],
            "tax_percentage": ["pyint", {"min_value": 0, "max_value": 20}],
            "total_cost": ["pyint", {"min_value": 200, "max_value": 4000}],
            "copay_details": ["sentence", {"nb_words": 5}],
            "emergency_contact": "phone_number",
        }


class AutoInsurance(BaseSchema):
    """Fields specific to an auto insurance policy."""

    def get_fields(self) -> SchemaDefinition:
        return {
            "policy_id": "uuid4",
            "holder_name": "name",
            "vin": "vin",
            "license_plate": "license_plate",
            "vehicle_model": "vehicle_model",
            "premium_amount": ["pyint", {"min_value": 200, "max_value": 2000}],
            "tax_percentage": ["pyint", {"min_value": 0, "max_value": 20}],
            "total_cost": ["pyint", {"min_value": 200, "max_value": 4000}],
            "policy_limit": ["pyint", {"min_value": 5000, "max_value": 100000}],
            "coverage_type": ["random_element", {"elements": ["Comprehensive","Liability","Collision"]}],
        }


class LifeInsurance(BaseSchema):
    """Fields specific to a life insurance policy."""

    def get_fields(self) -> SchemaDefinition:
        return {
            "policy_id": "uuid4",
            "holder_name": "name",
            "beneficiary_name": "name",
            "coverage_amount": ["pyint", {"min_value": 50000, "max_value": 500000}],
            "premium_amount": ["pyint", {"min_value": 200, "max_value": 2000}],
            "tax_percentage": ["pyint", {"min_value": 0, "max_value": 20}],
            "total_cost": ["pyint", {"min_value": 200, "max_value": 4000}],
        }


class HomeInsurance(BaseSchema):
    """Fields specific to a home insurance policy."""

    def get_fields(self) -> SchemaDefinition:
        return {
            "policy_id": "uuid4",
            "holder_name": "name",
            "property_address": "address",
            "square_footage": ["pyint", {"min_value": 800, "max_value": 5000}],
            "premium_amount": ["pyint", {"min_value": 200, "max_value": 2000}],
            "tax_percentage": ["pyint", {"min_value": 0, "max_value": 20}],
            "total_cost": ["pyint", {"min_value": 200, "max_value": 4000}],
            "dwelling_coverage": ["pyint", {"min_value": 50000, "max_value": 500000}],
            "year_built": ["pyint", {"min_value": 1900, "max_value": 2023}],
        }


# Registry that maps the UI‑friendly type string to its schema instance.
SCHEMA_REGISTRY: Dict[str, BaseSchema] = {
    "MedicalInsurance": MedicalInsurance(),
    "AutoInsurance": AutoInsurance(),
    "LifeInsurance": LifeInsurance(),
    "HomeInsurance": HomeInsurance(),
}


def get_schema(type_str: str) -> Optional[BaseSchema]:
    """Return the schema for the given policy type, or None if unknown."""
    return SCHEMA_REGISTRY.get(type_str)
