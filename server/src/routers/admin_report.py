from fastapi import APIRouter, Depends, HTTPException, Security, UploadFile, File, Form
from fastapi.responses import ORJSONResponse
from fastapi.security.api_key import APIKeyHeader
import json
from src.config import settings
from src.schemas.admin_report import ReportInput
from src.schemas.report import Report
from src.services.report_launcher import launch_report_generation
from src.services.report_status import load_status_as_reports
from src.utils.logger import setup_logger

slogger = setup_logger()
router = APIRouter()


api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


async def verify_admin_api_key(api_key: str = Security(api_key_header)):
    if not api_key or api_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key


@router.get("/admin/reports")
async def get_reports(api_key: str = Depends(verify_admin_api_key)) -> list[Report]:
    return load_status_as_reports()



@router.post("/admin/reports", status_code=202)
async def create_report(
    report_input_json: str = Form(...),
    file: UploadFile = File(None),
    pi_key: str = Depends(verify_admin_api_key)
    ):
    """_summary_

    Args:
        report_input_json (Form): _description_
        file (UploadFile, optional): _description_. Defaults to File(None).
        pi_key (str, optional): _description_. Defaults to Depends(verify_admin_api_key).

    Raises:
        HTTPException: _description_
        HTTPException: _description_

    Returns:
        _type_: _description_
        
    ```Sample Input
    {
        "prompt": {
            "extraction": "
            You are an expert research assistant to help create a dataset of organized discussions. 
            You will be provided with example discussions from members of the public, and you will organize them into a more thoughtful and readable form. If necessary, you can split it into two or more separate discussions, but in many cases it will be better to think of it as a single discussion. Return the results as a JSON list of strings. Write the summary in Japanese.",
            "initialLabelling": "labeling prompt",
            "mergeLabelling": "merge prpmpt",
            "overview": "overview prompt"
        },
        "inputType": "spreadsheet",
        "question": "test",
        "model": "gpt-4o-mini",
        "input": "random-id-test",
        "intro": "test intro",
        "cluster": [5, 50],
        "workers": 5,
        "spreadsheet_url": "https://docs.google.com/spreadsheets/d/1a5RgbAh9nAuPATgigG3WtPhzTkD7pZyGlVu5ARFjzfw/edit?usp=sharing"
        }

    """
    try:
        report = json.loads(report_input_json)
        report = ReportInput(**report)
        
        launch_report_generation(file, report)
        return ORJSONResponse(
            content=None,
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
        )
    except ValueError as e:
        slogger.error(f"ValueError: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        slogger.error(f"Exception: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e
    
# @router.post("/admin/reports", status_code=202)
# async def create_report(report: ReportInput, api_key: str = Depends(verify_admin_api_key)):
#     try:
#         launch_report_generation(report)
#         return ORJSONResponse(
#             content=None,
#             headers={
#                 "Content-Type": "application/json",
#                 "Access-Control-Allow-Origin": "*",
#             },
#         )
#     except ValueError as e:
#         slogger.error(f"ValueError: {e}", exc_info=True)
#         raise HTTPException(status_code=400, detail=str(e)) from e
#     except Exception as e:
#         slogger.error(f"Exception: {e}", exc_info=True)
#         raise HTTPException(status_code=500, detail="Internal server error") from e
