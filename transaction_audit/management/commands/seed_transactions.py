from django.core.management.base import BaseCommand
import random
from transaction_audit.models import Transaction

class Command(BaseCommand):
    help = 'Seeds the database with dummy transaction data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')

        self.seed_transactions()
        self.stdout.write('Database seeding complete.')

    def seed_transactions(self):
        merchants = ['Merchant A', 'Merchant B', 'Merchant C', 'Merchant D']

        transactions = []

        for _ in range(10000):
            transaction = Transaction(
                amount=round(random.uniform(1.00, 9999.99), 2),
                merchant=random.choice(merchants),
                is_flagged=random.choice([True, False]),
            )
            transactions.append(transaction)

        Transaction.objects.bulk_create(transactions)
    