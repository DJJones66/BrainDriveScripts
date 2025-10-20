#!/usr/bin/env python3
"""
Developer helper script for uninstalling BrainDrive plugins.

Usage:
    python dev_delete.py                 # Uninstall InfiniteCraft (default slug)
    python dev_delete.py --slug MyPlugin # Uninstall plugin by slug
    python dev_delete.py --id <plugin_id> # Uninstall plugin using plugin id (userId_slug)
"""

import argparse
from typing import Optional

import requests

from dev_install import login_and_get_token, BASE_URL

USER_EMAIL = "aaaa@gmail.com"
USER_PASSWORD = "10012002"


def extract_slug(plugin_id: str) -> str:
  """Convert plugin id of form '<user>_<slug>' into slug."""
  parts = plugin_id.split('_')
  if len(parts) >= 2:
    return '_'.join(parts[1:])
  return plugin_id


def delete_plugin(plugin_slug: str):
  token = login_and_get_token()
  headers = {"Authorization": f"Bearer {token}"}
  endpoint = f"{BASE_URL}/api/v1/plugins/{plugin_slug}/uninstall"
  print(f"➤ Deleting plugin '{plugin_slug}' via {endpoint}")

  response = requests.delete(endpoint, headers=headers, timeout=60)
  try:
    response.raise_for_status()
  except requests.HTTPError as exc:
    print(f"❌ Plugin deletion failed: {exc}")
    try:
      print("Server response:", response.json())
    except Exception:
      print("Server response text:", response.text)
    raise

  print("✅ Plugin deletion request succeeded.")
  try:
    print("Server response:", response.json())
  except Exception:
    print("Server response text:", response.text)


def main():
  parser = argparse.ArgumentParser(description="Uninstall a BrainDrive plugin via API.")
  parser.add_argument("--slug", help="Plugin slug to uninstall (e.g., InfiniteCraft)")
  parser.add_argument("--id", help="Plugin ID to uninstall (format: <user_id>_<plugin_slug>)")
  args = parser.parse_args()

  plugin_slug: Optional[str] = None

  if args.id:
    plugin_slug = extract_slug(args.id)
  elif args.slug:
    plugin_slug = args.slug
  else:
    plugin_slug = "InfiniteCraft"

  delete_plugin(plugin_slug)


if __name__ == "__main__":
  main()
