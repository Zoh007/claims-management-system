from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from claims.models import Claim, ClaimDetail, Flag, Note
import csv
import io
import os
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Optional


class Command(BaseCommand):
    help = 'Load sample claims data from CSV files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before loading',
        )
        parser.add_argument('--csv-list', dest='csv_list', default='claim_list_data.csv', help='Path to claim list CSV')
        parser.add_argument('--csv-detail', dest='csv_detail', default='claim_detail_data.csv', help='Path to claim detail CSV')
        parser.add_argument('--samples', dest='samples', action='store_true', help='(Optional) create demo flags and notes')
        parser.add_argument('--append', dest='append', action='store_true', help='Append-only: create new rows; do not update existing')
        parser.add_argument('--batch-size', dest='batch_size', default=1000, type=int, help='Batch size for operations (default 1000)')
        parser.add_argument('--quiet', dest='quiet', action='store_true', help='Reduce logging (summary only)')

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Claim.objects.all().delete()
            ClaimDetail.objects.all().delete()
            Flag.objects.all().delete()
            Note.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared'))

        # Ensure a default admin user exists and is usable (reset each run for dev convenience)
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        # Always enforce admin flags and reset password for local/dev usage
        user.is_staff = True
        user.is_superuser = True
        user.email = user.email or 'admin@example.com'
        user.first_name = user.first_name or 'Admin'
        user.last_name = user.last_name or 'User'
        user.set_password('admin123')
        user.save()
        if created:
            self.stdout.write(self.style.SUCCESS('Created default admin user (username: admin, password: admin123)'))
        else:
            self.stdout.write(self.style.SUCCESS('Reset default admin credentials (username: admin, password: admin123)'))

        # Load claims from provided CSV
        self.load_claims(options.get('csv_list'), append=options.get('append', False), batch_size=options.get('batch_size', 1000), quiet=options.get('quiet', False))
        
        # Load claim details from provided CSV
        self.load_claim_details(options.get('csv_detail'), append=options.get('append', False), batch_size=options.get('batch_size', 1000), quiet=options.get('quiet', False))
        
        # Optionally add demo flags and notes when --samples is provided
        if options.get('samples'):
            self.add_sample_flags_and_notes()
        
        self.stdout.write(self.style.SUCCESS('Sample data loaded successfully!'))

    def _parse_money(self, value: str) -> Decimal:
        if value is None:
            return Decimal('0')
        txt = str(value).strip().replace('$', '').replace(',', '')
        if txt == '':
            return Decimal('0')
        try:
            return Decimal(txt)
        except InvalidOperation:
            return Decimal('0')

    def _parse_date(self, value: str):
        if not value:
            return None
        for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', '%Y/%m/%d'):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        return None

    def _open_reader(self, csv_file: str) -> csv.DictReader:
        """Create a DictReader over the file contents with auto delimiter detection.
        Reads the file into memory to avoid dangling file handles.
        """
        with open(csv_file, 'r', encoding='utf-8') as f:
            data = f.read()
        sample = data[:2048]
        delimiter = '|'
        try:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample, delimiters='|,\t')
            delimiter = dialect.delimiter
        except Exception:
            pass
        return csv.DictReader(io.StringIO(data), delimiter=delimiter)

    def _get(self, row_map: dict, candidates: list[str]) -> Optional[str]:
        for key in candidates:
            if key in row_map:
                return row_map.get(key)
        return None

    def load_claims(self, csv_file: Optional[str], append: bool = False, batch_size: int = 1000, quiet: bool = True):
        csv_file = csv_file or 'claim_list_data.csv'
        if not os.path.exists(csv_file):
            self.stdout.write(self.style.WARNING(f'CSV file {csv_file} not found'))
            return

        self.stdout.write('Loading claims from CSV...')
        
        reader = self._open_reader(csv_file)
        imported = 0
        for row in reader:
                try:
                    # normalize keys once per row
                    row_l = { (k or '').strip().lower(): (v or '').strip() for k, v in row.items() }
                    discharge_date = self._parse_date(self._get(row_l, ['discharge_date', 'discharge date', 'date']))
                    
                    billed = self._parse_money(self._get(row_l, ['billed_amount', 'billed']))
                    paid = self._parse_money(self._get(row_l, ['paid_amount', 'paid']))
                    status = (self._get(row_l, ['status']) or 'Pending')
                    patient = (self._get(row_l, ['patient_name', 'patient']) or 'Unknown Patient')
                    insurer = (self._get(row_l, ['insurer_name', 'insurer']) or 'Unknown Insurer')
                    claim_id_value = self._get(row_l, ['id', 'claim_id', 'claim id', 'claimid'])
                    if not claim_id_value:
                        raise ValueError('Missing claim id')

                    if append and Claim.objects.filter(claim_id=claim_id_value).exists():
                        if not quiet:
                            self.stdout.write(f'Skipped existing claim (append mode): {claim_id_value}')
                        continue

                    if append:
                        claim, created = Claim.objects.get_or_create(
                            claim_id=claim_id_value,
                            defaults={
                                'patient_name': patient,
                                'billed_amount': billed,
                                'paid_amount': paid,
                                'status': status,
                                'insurer_name': insurer,
                                'discharge_date': discharge_date or timezone.now().date(),
                            }
                        )
                        if not quiet:
                            self.stdout.write(('Created' if created else 'Exists') + f' claim: {claim.claim_id}')
                    else:
                        claim, created = Claim.objects.update_or_create(
                            claim_id=claim_id_value,
                            defaults={
                                'patient_name': patient,
                                'billed_amount': billed,
                                'paid_amount': paid,
                                'status': status,
                                'insurer_name': insurer,
                                'discharge_date': discharge_date or timezone.now().date(),
                            }
                        )
                        if not quiet:
                            self.stdout.write(('Created' if created else 'Updated') + f' claim: {claim.claim_id}')
                    imported += 1
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing row {row}: {e}'))
        self.stdout.write(self.style.SUCCESS(f'Claims imported/updated: {imported}'))

    def load_claim_details(self, csv_file: Optional[str], append: bool = False, batch_size: int = 1000, quiet: bool = True):
        csv_file = csv_file or 'claim_detail_data.csv'
        if not os.path.exists(csv_file):
            self.stdout.write(self.style.WARNING(f'CSV file {csv_file} not found'))
            return

        self.stdout.write('Loading claim details from CSV...')
        
        reader = self._open_reader(csv_file)
        linked, missing = 0, 0
        for row in reader:
                try:
                    row_l = { (k or '').strip().lower(): (v or '').strip() for k, v in row.items() }
                    claim_id_value = self._get(row_l, ['claim_id', 'id', 'claim id', 'claimid'])
                    # Find the corresponding claim
                    claim = Claim.objects.filter(claim_id=claim_id_value).first()
                    if not claim:
                        if not quiet:
                            self.stdout.write(self.style.WARNING(f'Claim {claim_id_value} not found, skipping detail'))
                        missing += 1
                        continue
                    
                    cpt_codes = self._get(row_l, ['cpt_codes', 'cpt', 'codes']) or ''
                    denial_reason = self._get(row_l, ['denial_reason', 'denial', 'reason']) or ''

                    if append and ClaimDetail.objects.filter(claim=claim).exists():
                        if not quiet:
                            self.stdout.write(f'Skipped existing detail (append mode): {claim.claim_id}')
                        created = False
                    else:
                        detail, _created = ClaimDetail.objects.get_or_create(claim=claim)
                        detail.cpt_codes = cpt_codes
                        detail.denial_reason = denial_reason
                        detail.save()
                        created = _created
                    
                    if not quiet:
                        if created:
                            self.stdout.write(f'Created detail for claim: {claim.claim_id}')
                        else:
                            self.stdout.write(f'Updated detail for claim: {claim.claim_id}')
                    linked += 1
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing detail row {row}: {e}'))
        self.stdout.write(self.style.SUCCESS(f'Claim details linked: {linked}; missing references: {missing}'))

    def add_sample_flags_and_notes(self):
        self.stdout.write('Adding sample flags and notes...')
        
        # Get the admin user
        admin_user = User.objects.filter(username='admin').first()
        if not admin_user:
            self.stdout.write(self.style.WARNING('Admin user not found, skipping flags and notes'))
            return
        
        # Get some claims to add flags and notes to
        claims = Claim.objects.all()[:5]
        
        for i, claim in enumerate(claims):
            # Add a flag
            flag_reasons = [
                'Underpayment investigation needed',
                'Documentation review required',
                'Billing discrepancy detected',
                'Insurance verification pending',
                'Claim requires medical review'
            ]
            
            flag = Flag.objects.create(
                claim=claim,
                user=admin_user,
                reason=flag_reasons[i % len(flag_reasons)]
            )
            self.stdout.write(f'Added flag: {flag.reason}')
            
            # Add a note
            note_content = f'Sample note for claim {claim.claim_id}. This claim requires attention due to {flag.reason.lower()}.'
            
            note = Note.objects.create(
                claim=claim,
                user=admin_user,
                content=note_content
            )
            self.stdout.write(f'Added note for claim: {claim.claim_id}')
