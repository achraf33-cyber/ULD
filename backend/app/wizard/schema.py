"""Hardware targets available for the create-instance wizard."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from app.schemas import Backend


class WizardHardware(BaseModel):
    """One physical GPU the wizard can bind a new instance to."""

    id: str
    vendor: str
    backend: Backend
    name: str
    pci_slot: str
    driver: str
    cuda_index: Optional[int] = None
    mem_used_mb: Optional[float] = None
    mem_total_mb: Optional[float] = None
    mem_free_mb: Optional[float] = None
    effort_percent: Optional[float] = None
    core_count: Optional[int] = None
    product_family: Optional[str] = None
    creatable: bool = True
    note: Optional[str] = None
    available: bool = True
    availability_note: Optional[str] = None
    instances_on_gpu: list[str] = []
    render_node: Optional[str] = None
    supported_apis: list[str] = []
    available_compute_backends: list[str] = []
    compute_backend: str = "cuda"
    device_id: Optional[str] = None
