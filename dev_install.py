#!/usr/bin/env python3
"""
Developer helper script for building and installing the Infinite Craft plugin.

Usage:
    python dev_install.py           # Build archive and install via API
    python dev_install.py --build   # Only build archive
    python dev_install.py --install # Only install (assumes archive exists)

Configuration:
    Adjust USER_EMAIL, USER_PASSWORD, and BASE_URL as needed.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

import requests

PLUGIN_DIR = Path(__file__).resolve().parent
PLUGIN_NAME = "BrainDrive-InfiniteCraft-Community-Plugin"
PLUGIN_VERSION = "1.0.0"
ARCHIVE_NAME = f"{PLUGIN_NAME}-v{PLUGIN_VERSION}.tar.gz"

USER_EMAIL = "aaaa@gmail.com"
USER_PASSWORD = "10012002"
BASE_URL = "http://localhost:8205"

LOGIN_ENDPOINT = f"{BASE_URL}/api/v1/auth/login"
INSTALL_ENDPOINT = f"{BASE_URL}/api/v1/plugins/install"


def run_command(command, cwd: Optional[str] = None):
  print(f"➤ Running: {' '.join(command)}")
  subprocess.check_call(command, cwd=cwd)


def clean_pycache():
  """Remove __pycache__ directories to avoid packaging stale bytecode."""
  for cache_dir in (PLUGIN_DIR / PLUGIN_NAME).rglob("__pycache__"):
    shutil.rmtree(cache_dir, ignore_errors=True)


def build_archive():
  clean_pycache()
  run_command(["./build_archive.py", PLUGIN_NAME, PLUGIN_VERSION], cwd=str(PLUGIN_DIR))


def login_and_get_token() -> str:
  payload = {"email": USER_EMAIL, "password": USER_PASSWORD}
  print(f"➤ Logging in as {USER_EMAIL}")
  response = requests.post(LOGIN_ENDPOINT, json=payload, timeout=30)
  response.raise_for_status()
  data = response.json()
  token = data.get("access_token")
  if not token:
    raise RuntimeError("Login response did not include access_token.")
  return token


def install_plugin():
  archive_path = PLUGIN_DIR / ARCHIVE_NAME
  if not archive_path.exists():
    raise FileNotFoundError(f"Archive not found: {archive_path}. Build it first.")

  token = login_and_get_token()
  headers = {"Authorization": f"Bearer {token}"}

  print(f"➤ Uploading {archive_path.name} to {INSTALL_ENDPOINT}")
  with archive_path.open("rb") as archive_file:
    files = {"file": (archive_path.name, archive_file, "application/gzip")}
    data = {
      "method": "local-file",
      "filename": archive_path.name,
    }
    response = requests.post(
      INSTALL_ENDPOINT,
      headers=headers,
      data=data,
      files=files,
      timeout=180,
    )

  try:
    response.raise_for_status()
  except requests.HTTPError as exc:
    print(f"❌ Installation request failed: {exc}")
    try:
      print("Server response:", response.json())
    except Exception:
      print("Server response text:", response.text)
    raise

  print("✅ Installation request succeeded.")
  print("Server response:", response.json())


def main():
  parser = argparse.ArgumentParser(description="Build and install Infinite Craft plugin.")
  parser.add_argument("--build", action="store_true", help="Only build the plugin archive.")
  parser.add_argument("--install", action="store_true", help="Only install the plugin (requires archive).")
  args = parser.parse_args()

  if args.build:
    build_archive()
    return

  if args.install:
    install_plugin()
    return

  build_archive()
  install_plugin()


if __name__ == "__main__":
  main()
