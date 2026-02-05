from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipelines.ingest.ingest_orders import run as ingest_orders
from pipelines.ingest.ingest_customers import run as ingest_customers
from pipelines.ingest.ingest_products import run as ingest_products
from pipelines.ingest.ingest_shipping import run as ingest_shipping
from pipelines.ingest.ingest_web_events import run as ingest_web_events
from pipelines.ingest.ingest_payments import run as ingest_payments
from pipelines.transform.staging_transform import run as staging_transform
from pipelines.quality.quality_checks import run as quality_checks


if __name__ == "__main__":
    ingest_orders()
    ingest_customers()
    ingest_products()
    ingest_shipping()
    ingest_web_events()
    ingest_payments()
    staging_transform()
    quality_checks()
    print("RetailPulse pipeline finished.")