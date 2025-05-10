# app/main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
import shutil, os, uuid

from processor import (
    process_files,
    build_transaction_circle,
    merge_and_count_duplicates,
    match_r_column
)

app = FastAPI()

# 公开静态目录，让用户能下载 zip 文件
app.mount("/downloads", StaticFiles(directory="app/static/downloads"), name="downloads")

@app.post("/process")
async def process_uploaded_files(files: list[UploadFile] = File(...)):
    session_id = str(uuid.uuid4())
    base_path = f"app/uploads/{session_id}"
    os.makedirs(base_path, exist_ok=True)

    # 保存上传的文件
    for file in files:
        dest_path = os.path.join(base_path, file.filename)
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    # 创建输出目录
    dest_folder = os.path.join(base_path, "结果/原文件")
    name_folder = os.path.join(base_path, "结果/姓名库")
    circle_folder = os.path.join(base_path, "结果/交易圈")

    try:
        # 调用你的处理逻辑
        process_files(base_path, dest_folder, name_folder)
        build_transaction_circle(dest_folder, circle_folder)
        merge_and_count_duplicates(circle_folder, dest_folder)
        match_r_column(dest_folder)
    except Exception as e:
        return {"status": "failed", "error": str(e)}

    # 打包 zip 文件
    zip_path = shutil.make_archive(
        base_name=os.path.join(base_path, "results"),
        format="zip",
        root_dir=os.path.join(base_path, "结果")
    )

    # 将 zip 文件复制到公开目录
    final_zip_path = f"app/static/downloads/{session_id}.zip"
    os.makedirs(os.path.dirname(final_zip_path), exist_ok=True)
    shutil.copyfile(zip_path, final_zip_path)

    # 返回结果 zip 的下载链接（相对路径，供 Dify 拼接）
    return {
        "status": "success",
        "download_url": f"/downloads/{session_id}.zip"
    }