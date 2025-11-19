"""Error messages and error handling utilities."""
from typing import Dict, Any


ERROR_MESSAGES: Dict[str, Dict[str, str]] = {
    "invalid_file_format": {
        "message": "アップロードされたファイルはPDF形式ではありません",
        "suggestion": "PDFファイルを選択してください"
    },
    "file_too_large": {
        "message": "ファイルサイズが制限を超えています",
        "suggestion": "50MB以下のファイルを選択してください"
    },
    "insufficient_reference_points": {
        "message": "基準点が不足しています（現在: {count}個）",
        "suggestion": "最低3つの基準点を設定してください"
    },
    "collinear_points": {
        "message": "基準点が一直線上に配置されています",
        "suggestion": "基準点を三角形状に配置してください"
    },
    "no_boxes_detected": {
        "message": "赤枠が検出されませんでした",
        "suggestion": "PDF画像に赤枠が含まれているか確認してください"
    },
    "file_not_found": {
        "message": "指定されたファイルが見つかりません",
        "suggestion": "ファイルIDを確認してください"
    },
    "pdf_conversion_failed": {
        "message": "PDFの画像変換に失敗しました",
        "suggestion": "有効なPDFファイルであることを確認してください"
    },
    "image_processing_failed": {
        "message": "画像処理中にエラーが発生しました",
        "suggestion": "画像ファイルが破損していないか確認してください"
    },
    "transformation_failed": {
        "message": "座標変換に失敗しました",
        "suggestion": "基準点の配置を確認してください"
    },
    "kml_generation_failed": {
        "message": "KMLファイルの生成に失敗しました",
        "suggestion": "変換された座標データを確認してください"
    },
    "invalid_coordinates": {
        "message": "無効な座標値が入力されました",
        "suggestion": "緯度は-90〜90度、経度は-180〜180度の範囲で入力してください"
    },
    "internal_error": {
        "message": "内部エラーが発生しました",
        "suggestion": "しばらく時間をおいて再度お試しください"
    }
}


def get_error_message(error_type: str, **kwargs: Any) -> Dict[str, str]:
    """
    Get formatted error message.
    
    Args:
        error_type: Error type key
        **kwargs: Format parameters for the message
        
    Returns:
        Dictionary with error, message, and suggestion
    """
    if error_type not in ERROR_MESSAGES:
        error_type = "internal_error"
    
    error_info = ERROR_MESSAGES[error_type].copy()
    
    # Format message with provided parameters
    if kwargs:
        error_info["message"] = error_info["message"].format(**kwargs)
    
    return {
        "error": error_type,
        "message": error_info["message"],
        "suggestion": error_info["suggestion"]
    }
