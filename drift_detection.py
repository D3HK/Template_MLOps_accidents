import pandas as pd
from evidently.report import Report
from evidently.metrics import DataDriftTable

# Загрузка данных из вашей структуры
reference_data = pd.read_csv("data/preprocessed/X_train.csv")  # Эталон
current_data = pd.read_csv("data/preprocessed/X_test.csv")      # Текущие данные

# Проверка дрейда
report = Report(metrics=[DataDriftTable()])
report.run(
    current_data=current_data,
    reference_data=reference_data,
    column_mapping=None  # Автоопределение фичей
)

# Сохранение отчета в папку reports
report.save_html("reports/drift_report.html")