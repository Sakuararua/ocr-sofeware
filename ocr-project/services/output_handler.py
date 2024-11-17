import csv

def save_results_to_csv(results, output_path):
    """
    保存结果到 CSV 文件
    """
    if not results:
        print("没有结果需要保存")
        return

    keys = ["image_name", "快递单号", "收件人姓名", "地址", "联系方式"]
    with open(output_path, mode="w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)
    print(f"结果已保存到 {output_path}")
