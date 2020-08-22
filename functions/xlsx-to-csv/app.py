import os
import boto3
import openpyxl
import csv

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    data_target_bucket = os.environ['DATA_TARGET_BUCKET']            # 環境変数より変換後データ保存先バケット取得
    data_source_bucket = event['Records'][0]['s3']['bucket']['name'] # Lambda関数呼び出し元バケット名
    data_source_key = event['Records'][0]['s3']['object']['key']     # オブジェクトキー取得

    # カレントディレクトリ移動
    os.chdir('/tmp')

    # S3にPUTされたExcelファイルダウンロード
    source_bucket_obj = s3.Bucket(data_source_bucket)
    source_bucket_obj.download_file(data_source_key, data_source_key)

    # Excel Book/Worksheetオープン
    wb = openpyxl.load_workbook(data_source_key)
    ws = wb.worksheets[0]

    # CSVファイル名
    csv_filename = os.path.splitext(os.path.basename(data_source_key))[0] + '.csv'

    # CSVファイル作成
    with open(csv_filename, 'w', newline="") as csvfile:
        writer = csv.writer(csvfile)
        for row in ws.rows:
            # Excel行データをリスト形式で取得
            row_data = [cell.value for cell in row]
            # CSV書き込み
            writer.writerow(row_data)

    # CSVファイルアップロード
    s3_client.upload_file(csv_filename, data_target_bucket, csv_filename)

    return None




