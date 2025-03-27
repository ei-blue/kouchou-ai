import json, csv, io, os
import subprocess
import threading
from pathlib import Path
from typing import Any

import pandas as pd
from src.config import settings
from src.schemas.admin_report import ReportInput
from src.services.report_status import add_new_report_to_status, set_status
from src.services.spreadsheet_service import delete_input_file, process_spreadsheet_url
from src.schemas.admin_report import Comment


def _build_config(report_input: ReportInput, comment_num) -> dict[str, Any]:
    # comment_num = len(report_input.comments)

    config = {
        "name": report_input.input,
        "input": report_input.input,
        "question": report_input.question,
        "intro": report_input.intro,
        "model": report_input.model,
        "extraction": {
            "prompt": report_input.prompt.extraction,
            "workers": report_input.workers,
            "limit": comment_num,
        },
        "hierarchical_clustering": {
            "cluster_nums": report_input.cluster,
        },
        "hierarchical_initial_labelling": {
            "prompt": report_input.prompt.initial_labelling,
            "sampling_num": 30,
            "workers": report_input.workers,
        },
        "hierarchical_merge_labelling": {
            "prompt": report_input.prompt.merge_labelling,
            "sampling_num": 30,
            "workers": report_input.workers,
        },
        "hierarchical_overview": {"prompt": report_input.prompt.overview},
        "hierarchical_aggregation": {
            "sampling_num": report_input.workers,
        },
    }
    return config


def save_config_file(report_input: ReportInput, comment_num: int) -> Path:
    config = _build_config(report_input, comment_num)
    config_path = settings.CONFIG_DIR / f"{report_input.input}.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    return config_path


def save_input_file(file, report_input: ReportInput) -> int:
    """
    入力データをCSVファイルとして保存する

    Args:
        report_input: レポート生成の入力データ

    Returns:
        Path: 保存されたCSVファイルのパス
    """
    # TODO update
    # はやい段階で少しのデータでバリデーションをする
    # report_input = 'test_filename'
    file_name = report_input.input
    input_path = settings.INPUT_DIR / f"{file_name}_cleaned.csv"
    
    if report_input.inputType == "spreadsheet":
        
        # if os.path.exists(input_path):
        #     return input_path
        
        original_path = process_spreadsheet_url(report_input.spreadsheet_url, file_name)
        # スプシCSVを読み込む
        header_df = pd.read_csv(original_path, nrows=0)
        available_columns = header_df.columns.tolist()
    
        # 指定したカラムのうち、実際に存在するカラムだけを抽出
        use_cols = [col for col in Comment.__fields__.keys() if col in available_columns]
        
        if 'comment' not in use_cols:
            raise ValueError("スプレッドシートには 'comment' または 'comment-body' カラムが必要です")
        df = pd.read_csv(original_path, usecols=use_cols)
    else:
        # CSVファイルの場合の処理
        contents = file.read()
        decoded = contents.decode('utf-8')        
        # ヘッダー行のみを読み込んで利用可能なカラムを取得
        header_df = pd.read_csv(io.StringIO(decoded), nrows=0)
        available_columns = header_df.columns.tolist()
    
        # 指定したカラムのうち、実際に存在するカラムだけを抽出
        use_cols = [col for col in Comment.__fields__.keys() if col in available_columns]
        
        if 'comment' not in use_cols:
            raise ValueError("スプレッドシートには 'comment' または 'comment-body' カラムが必要です")        
        # 存在するカラムだけを使ってCSVを読み込む
        df = pd.read_csv(io.StringIO(decoded), usecols=use_cols)
  
    if 'id' not in df.columns:
        # TODO update id logic
        df['id'] = [f"id-{i + 1}" for i in range(len(df))]
  
    df.to_csv(input_path, index=False)
    return len(df)


def _monitor_process(process: subprocess.Popen, slug: str) -> None:
    """
    サブプロセスの実行を監視し、完了時にステータスを更新する

    Args:
        process: 監視対象のサブプロセス
        slug: レポートのスラッグ
    """
    retcode = process.wait()
    if retcode == 0:
        set_status(slug, "ready")
    else:
        set_status(slug, "error")


def launch_report_generation(file, report_input: ReportInput) -> None:
    """
    外部ツールの main.py を subprocess で呼び出してレポート生成処理を開始する関数。
    """
    try:
        add_new_report_to_status(report_input)
        comment_num = save_input_file(file, report_input)
        config_path = save_config_file(report_input, comment_num)
        cmd = ["python", "hierarchical_main.py", config_path, "--skip-interaction", "--without-html"]
        execution_dir = settings.TOOL_DIR / "pipeline"
        process = subprocess.Popen(cmd, cwd=execution_dir)
        threading.Thread(target=_monitor_process, args=(process, report_input.input), daemon=True).start()
    except Exception as e:
        set_status(report_input.input, "error")
        raise e
