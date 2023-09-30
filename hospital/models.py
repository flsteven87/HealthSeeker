from django.db import models

class Hospital(models.Model):
    # 使用 CharField 來儲存小到中型的字串，IntegerField 儲存整數，DateField 儲存日期
    # 當資料欄位有可能是空值時，設定 null=True, blank=True
    
    # 分區別
    area_code = models.IntegerField(verbose_name="分區別")
    
    # 醫事機構代碼
    hospital_id = models.CharField(max_length=15, primary_key=True, verbose_name="醫事機構代碼")
    
    # 醫事機構名稱
    hospital_name = models.CharField(max_length=255, verbose_name="醫事機構名稱")
    
    # 機構地址
    address = models.TextField(verbose_name="機構地址")
    
    # 電話區域號碼
    phone_area_code = models.CharField(max_length=5, verbose_name="電話區域號碼")
    
    # 電話號碼
    phone_number = models.CharField(max_length=20, verbose_name="電話號碼")
    
    # 特約類別
    contract_type = models.CharField(max_length=5, verbose_name="特約類別")
    
    # 型態別
    type_code = models.CharField(max_length=5, verbose_name="型態別")
    
    # 醫事機構種類
    hospital_category = models.CharField(max_length=5, verbose_name="醫事機構種類")
    
    # 終止合約或歇業日期，這裡可以是日期型態，但需要確保資料中是實際日期或空值
    contract_end_date = models.DateField(null=True, blank=True, verbose_name="終止合約或歇業日期")
    
    # 開業狀況
    operation_status = models.CharField(max_length=5, verbose_name="開業狀況")
    
    # 原始合約起日
    contract_start_date = models.DateField(verbose_name="原始合約起日")
