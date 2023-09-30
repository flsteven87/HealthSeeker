import io
import requests
import zipfile
import pandas as pd
from django.core.management.base import BaseCommand
from hospital.models import Hospital

class Command(BaseCommand):
    help = 'Updates the Hospital data from the provided URL'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url= 'https://www.nhi.gov.tw/DL.aspx?sitessn=292&u=LzAwMS9VcGxvYWQvMjkyL3JlbGZpbGUvMC84NDY3L2hvc3Bic2Muemlw&n=aG9zcGJzYy56aXA%3d&ico%20=.zip'
        self.file_path = './HCO/data/'

    def download(self):
        print("Downloading...")
        response = requests.get(self.url, verify=False)
        if response.status_code == 200:
            zip_content = io.BytesIO(response.content)
            print("Download completed!")

            with zipfile.ZipFile(zip_content, 'r') as zip_ref:
                zip_ref.extractall(self.file_path)
            print("Decompression completed!")
        else:
            print("Status Code:", response.status_code)        

    def update_db(self):
        txt_filename = 'hospbsc.txt'
        df = pd.read_csv(self.file_path + txt_filename, delimiter=",", encoding="UTF-16LE")
        column_mapping = {
            '分區別': 'area_code',
            '醫事機構代碼': 'hospital_id',
            '醫事機構名稱': 'hospital_name',
            '機構地址': 'address',
            '電話區域號碼 ': 'phone_area_code',
            '電話號碼': 'phone_number',
            '特約類別': 'contract_type',
            '型態別': 'type_code',
            '醫事機構種類': 'hospital_category',
            '終止合約或歇業日期': 'contract_end_date',
            '開業狀況': 'operation_status',
            '原始合約起日': 'contract_start_date'
        }
        df = df.rename(columns=column_mapping)

        # Convert date columns
        df['contract_start_date'] = pd.to_datetime(df['contract_start_date'], format='%Y%m%d', errors='coerce')
        df['contract_end_date'] = pd.to_datetime(df['contract_end_date'], format='%Y%m%d', errors='coerce')

        # Replace NaT with None for contract_start_date and contract_end_date columns
        df['contract_start_date'] = df['contract_start_date'].where(df['contract_start_date'].notna(), None)
        df['contract_end_date'] = df['contract_end_date'].where(df['contract_end_date'].notna(), None)

        to_be_created = []
        to_be_updated = []

        # Get existing hospital_ids from the database
        existing_hospital_ids = set(Hospital.objects.values_list('hospital_id', flat=True))

        for index, row in df.iterrows():
            data = {
                'area_code': row['area_code'],
                'hospital_id': row['hospital_id'],
                'hospital_name': row['hospital_name'],
                'address': row['address'],
                'phone_area_code': row['phone_area_code'],
                'phone_number': row['phone_number'],
                'contract_type': row['contract_type'],
                'type_code': row['type_code'],
                'hospital_category': row['hospital_category'],
                'contract_end_date': None if pd.isna(row['contract_end_date']) else row['contract_end_date'],
                'operation_status': row['operation_status'],
                'contract_start_date': row['contract_start_date']
            }

            if row['hospital_id'] in existing_hospital_ids:
                instance = Hospital.objects.get(hospital_id=row['hospital_id'])
                for key, value in data.items():
                    setattr(instance, key, value)
                to_be_updated.append(instance)
            else:
                to_be_created.append(Hospital(**data))

        Hospital.objects.bulk_create(to_be_created)
        Hospital.objects.bulk_update(to_be_updated, [
            'area_code', 'hospital_name', 'address', 'phone_area_code',
            'phone_number', 'contract_type', 'type_code', 'hospital_category',
            'contract_end_date', 'operation_status', 'contract_start_date'
        ])


    def handle(self, *args, **kwargs):
        print('Updating 醫事機構代碼 metadata from 政府資料標準平台')
        self.download()
        self.update_db()
        print("Database update completed!")

