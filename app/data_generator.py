"""Agnostic synthetic data generator.

The PolicyGenerator reads a schema definition from schemas.py and
produces a list of dictionaries filled with fake data obtained via
Faker.
"""

from __future__ import annotations

from typing import Any, Dict, List

import warnings

from faker import Faker

from app.schemas import get_schema


class PolicyGenerator:
    """Core engine that creates synthetic insurance policies on the fly."""

    def generate_batch(self, policy_type: str, count: int) -> List[Dict[str, Any]]:
        """Return *count* fake policies conforming to *policy_type*.

        Parameters
        ----------
        policy_type : str
            One of the keys defined in ``SCHEMA_REGISTRY`` (e.g. "MedicalInsurance").
        count : int
            Number of policy objects to create (1–500 recommended).

        Returns
        -------
        List[Dict[str, Any]]
            Each dictionary contains the exact fields specified in the
            corresponding schema and filled with randomised Faker values.
        """
        schema = get_schema(policy_type)
        if schema is None:
            raise ValueError(f"Unknown policy type: {policy_type}")

        fields = schema.get_fields()
        fake = Faker('en_US')

        policies: List[Dict[str, Any]] = []

        for _ in range(count):
            policy: Dict[str, Any] = {}
            for field_name, field_def in fields.items():
                if isinstance(field_def, str):
                    # Simple Faker method call (no arguments)
                    try:
                        value = getattr(fake, field_def)()
                    except (AttributeError, TypeError, ValueError) as exc:
                        warnings.warn(f"Faker provider '{field_def}' raised {type(exc).__name__}, using 'N/A'")
                        value = "N/A"
                elif isinstance(field_def, (list, tuple)):
                    # First element is the method name, second (optional) is kwargs dict
                    method_name = field_def[0]
                    kwargs = field_def[1] if len(field_def) > 1 else {}
                    try:
                        value = getattr(fake, method_name)(**kwargs)
                    except (AttributeError, TypeError, ValueError) as exc:
                        warnings.warn(f"Faker provider '{method_name}' raised {type(exc).__name__}, using 'N/A'")
                        value = "N/A"
                else:
                    value = None  # Fallback – should never happen with current schemas
                policy[field_name] = value
            policies.append(policy)

        return policies
