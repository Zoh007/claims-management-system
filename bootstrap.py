#!/usr/bin/env python3
"""
One-shot project bootstrapper.

Runs migrations, loads CSV sample data, optionally cleans up CSVs, and starts the dev server.

Usage examples:
  python bootstrap.py                 # migrate, load CSVs, runserver
  python bootstrap.py --clear         # clear data then load fresh
  python bootstrap.py --cleanup       # delete CSVs after successful load
  python bootstrap.py --no-runserver  # setup only, do not run
  python bootstrap.py --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'claims_burger.settings')


def main() -> int:
    try:
        import django  # noqa: F401
    except Exception as exc:  # pragma: no cover
        print("Django is not installed. Run: pip install -r requirements.txt", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 1

    import django
    from django.core.management import call_command

    parser = argparse.ArgumentParser(description="Bootstrap the Claims app")
    parser.add_argument('--clear', action='store_true', help='Clear existing data before loading')
    parser.add_argument('--cleanup', action='store_true', help='Delete CSV files after successful load')
    parser.add_argument('--no-runserver', action='store_true', help='Do everything except runserver')
    parser.add_argument('--host', default='127.0.0.1', help='Host for runserver (default: 127.0.0.1)')
    parser.add_argument('--port', default='8000', help='Port for runserver (default: 8000)')
    parser.add_argument('--noreload', action='store_true', help='Disable Django auto-reloader to avoid double-run')
    parser.add_argument('--csv-list', default=str(BASE_DIR / 'claim_list_data.csv'), help='Path to claim list CSV')
    parser.add_argument('--csv-detail', default=str(BASE_DIR / 'claim_detail_data.csv'), help='Path to claim detail CSV')
    parser.add_argument('--append', action='store_true', help='Append-only: create new rows; do not update existing')
    parser.add_argument('--batch-size', default=1000, type=int, help='Batch size for operations (default 1000)')
    parser.add_argument('--verbose', action='store_true', help='Increase logging (default is quiet)')
    parser.add_argument('--samples', action='store_true', help='(Optional) create demo flags/notes during load')
    args = parser.parse_args()

    django.setup()

    # Avoid double-execution when Django auto-reloader spawns child process
    is_reloader_child = os.environ.get('RUN_MAIN') == 'true'
    if not is_reloader_child:
        print('Applying migrations...')
        call_command('migrate', interactive=False, verbosity=1)

        print('Loading sample data from CSV...')
        quiet = not args.verbose

        if args.clear:
            call_command('load_sample_data', clear=True, csv_list=args.csv_list, csv_detail=args.csv_detail, samples=args.samples, append=args.append, batch_size=args.batch_size, quiet=quiet, verbosity=1)
        else:
            call_command('load_sample_data', csv_list=args.csv_list, csv_detail=args.csv_detail, samples=args.samples, append=args.append, batch_size=args.batch_size, quiet=quiet, verbosity=1)

    # 3) Optionally remove CSVs
    if args.cleanup:
        for name in (args.csv_list, args.csv_detail):
            csv_path = Path(name)
            if csv_path.exists():
                try:
                    csv_path.unlink()
                    print(f'Removed {csv_path.name}')
                except Exception as exc:  # pragma: no cover
                    print(f'Warning: could not remove {csv_path}: {exc}', file=sys.stderr)

    # 4) Run server
    if not args.no_runserver:
        addr = f"{args.host}:{args.port}"
        print(f'Starting development server at http://{addr} ...')
        if args.noreload:
            call_command('runserver', addr, use_reloader=False)
        else:
            call_command('runserver', addr)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())


