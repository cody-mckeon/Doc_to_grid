import pytest
from src.grid_parser import _convert_to_export_url

def test_convert_url():
    url = "https://docs.google.com/document/d/ABC123/edit"
    assert _convert_to_export_url(url) == "https://docs.google.com/document/d/ABC123/export?format=txt"
