# -*- coding: utf-8 -*-
"""
Apple Health XML direct-to-database importer.
Parses Apple Health export.xml files and imports data directly to Django models.
"""
import logging
from xml.etree import ElementTree
from datetime import datetime

from django.contrib.auth import get_user_model
from healthstats.models import HeartRate, StepData, OxygenData

logger = logging.getLogger(__name__)
User = get_user_model()

# Mapping of Apple Health record types to Django models
RECORD_TYPE_MAPPING = {
    'HKQuantityTypeIdentifierHeartRate': {
        'model': HeartRate,
        'field_mapping': {
            'creation_date': 'creationDate',
            'start_date': 'startDate',
            'end_date': 'endDate',
            'value': 'value',
        }
    },
    'HKQuantityTypeIdentifierStepCount': {
        'model': StepData,
        'field_mapping': {
            'creation_date': 'creationDate',
            'start_date': 'startDate',
            'end_date': 'endDate',
            'value': 'value',
        }
    },
    'HKQuantityTypeIdentifierOxygenSaturation': {
        'model': OxygenData,
        'field_mapping': {
            'creation_date': 'creationDate',
            'start_date': 'startDate',
            'end_date': 'endDate',
            'value': 'value',
        }
    },
}


class AppleHealthXMLImporter:
    """
    Imports Apple Health XML data directly to Django models without CSV intermediary.
    """

    def __init__(self, xml_path, user):
        """
        Initialize importer with XML file path and user.

        Args:
            xml_path: Path to export.xml file
            user: Django User instance to associate records with
        """
        self.xml_path = xml_path
        self.user = user
        self.total_records_imported = 0
        self.records_by_type = {}

    def parse_xml(self):
        """
        Parse the Apple Health XML file.

        Returns:
            ElementTree root element

        Raises:
            FileNotFoundError: If XML file doesn't exist
            ElementTree.ParseError: If XML is malformed
        """
        try:
            tree = ElementTree.parse(self.xml_path)
            return tree.getroot()
        except FileNotFoundError:
            raise FileNotFoundError(f"Apple Health XML file not found: {self.xml_path}")
        except ElementTree.ParseError as e:
            raise ValueError(f"Failed to parse XML file: {str(e)}")

    def format_datetime(self, date_string):
        """
        Parse Apple Health datetime string to UTC datetime.

        Apple Health dates are formatted as: "YYYY-MM-DD HH:MM:SS TZ"
        Example: "2021-07-30 17:15:59 -0700"

        Args:
            date_string: Datetime string from Apple Health XML

        Returns:
            datetime object (timezone-aware)
        """
        try:
            # Parse with timezone info
            dt = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S %z")
            return dt
        except ValueError as e:
            logger.warning(f"Failed to parse datetime '{date_string}': {str(e)}")
            raise ValueError(f"Invalid datetime format: {date_string}")

    def import_records(self):
        """
        Parse XML and import all supported record types to database.

        Returns:
            Total number of records imported

        Raises:
            ValueError: If XML parsing fails or required fields are missing
        """
        logger.info(f"Starting import of Apple Health XML: {self.xml_path}")

        root = self.parse_xml()

        # Process each Record element
        for record_element in root.findall('Record'):
            record_type = record_element.get('type')

            if record_type in RECORD_TYPE_MAPPING:
                try:
                    self._process_record(record_element, record_type)
                except Exception as e:
                    logger.error(f"Error processing record of type {record_type}: {str(e)}")
                    # Continue with next record instead of failing entire import
                    continue

        logger.info(
            f"Completed import: {self.total_records_imported} total records imported. "
            f"Breakdown: {self.records_by_type}"
        )

        return self.total_records_imported

    def _process_record(self, record_element, record_type):
        """
        Process a single Record element and import to appropriate model.

        Args:
            record_element: XML Element of type 'Record'
            record_type: Value of the 'type' attribute (e.g., HKQuantityTypeIdentifierHeartRate)
        """
        config = RECORD_TYPE_MAPPING[record_type]
        model = config['model']
        field_mapping = config['field_mapping']

        # Extract attribute values from XML
        attrs = record_element.attrib

        # Build kwargs for model
        kwargs = {
            'author': self.user,
        }

        # Map XML attributes to model fields
        for model_field, xml_attr in field_mapping.items():
            if xml_attr not in attrs:
                raise ValueError(
                    f"Missing required attribute '{xml_attr}' in {record_type} record"
                )

            value = attrs[xml_attr]

            # Parse datetime fields
            if model_field in ('creation_date', 'start_date', 'end_date'):
                value = self.format_datetime(value)
            # Parse numeric fields
            elif model_field == 'value':
                try:
                    value = float(value)
                except ValueError:
                    raise ValueError(f"Invalid numeric value for {record_type}: {value}")

            kwargs[model_field] = value

        # Use get_or_create for idempotency
        obj, created = model.objects.get_or_create(**kwargs)

        if created:
            self.total_records_imported += 1
            record_type_short = record_type.replace('HKQuantityTypeIdentifier', '')
            self.records_by_type[record_type_short] = \
                self.records_by_type.get(record_type_short, 0) + 1
            logger.debug(f"Created {record_type_short} record")
        else:
            logger.debug(f"Skipped duplicate {record_type} record")
